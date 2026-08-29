#!/bin/bash
# VERIFY A REVIEW BUILD ON THE HANDSET. Not "it exported" — "it is installed, it booted, and it
# booted into the scene it was supposed to."
#
# WHY THIS EXISTS
# ---------------
# `build_review_app.sh --no-install` exiting 0 says the export -> xcodebuild chain ran. It says
# nothing about whether anything reached the device, and a session reported a build as
# "verified on device" on exactly that basis. It was not installed at all.
#
# This project already has the logged instance that makes the distinction non-negotiable: the
# Hollowmark ribbon was silent on device while every headless capture was clean, because NativeAOT
# had not registered the YAML DTOs. A build that compiles, exports, installs AND LAUNCHES can
# still do nothing — so the only evidence that counts is the app's own log, pulled back off the
# handset.
#
# It reports the three identifiers a walk needs to be evidence under LOOP-PROCESS §2.3:
#   BUNDLE ID   read off the DEVICE, not claimed by the app. An app asserting its own identity is
#               the weakest possible evidence of it.
#   BUILD       version/build as the device records it, plus the app's own builtAt stamp.
#   COMMIT      stamped into the review marker at build time and reported at boot.
#
# Usage:  tools/tier0_harness/verify_on_device.sh [--device <id-or-name>] [--bundle <id>]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEVICE="${TIER0_DEVICE:-}"
BUNDLE="${TIER0_BUNDLE_ID:-com.rafehatfield.catacombsofyarl.tier0}"
OUT="$ROOT/tools/tier1_floors/evidence"
CHECK_ONLY=""

while [ $# -gt 0 ]; do
	case "$1" in
		--device) DEVICE="$2"; shift 2 ;;
		--bundle) BUNDLE="$2"; shift 2 ;;
		--out)    OUT="$2"; shift 2 ;;
		# --check-log runs THE CHECKS ONLY, against a log already on disk, and touches no device.
		# It exists so the checks can be shown to FAIL — bible §13.5, no instrument's pass counts
		# until it has demonstrated it can fail — WITHOUT copying their expressions into a test.
		# A test that reimplements the thing it tests proves the reimplementation.
		--check-log) CHECK_ONLY="$2"; shift 2 ;;
		*) echo "unknown arg: $1" >&2; exit 2 ;;
	esac
done

if [ -n "$CHECK_ONLY" ]; then
	LOG="$CHECK_ONLY"
	[ -f "$LOG" ] || { echo "no such log: $LOG" >&2; exit 2; }
	echo "== CHECKS ONLY, against $LOG (no device touched)"
fi

if [ -z "$CHECK_ONLY" ]; then
# DEVICE RESOLUTION FROM STRUCTURED OUTPUT, NOT FROM COLUMNS.
#
# The first version parsed `devicectl list devices` with awk, taking $(NF-2) as the identifier.
# The Model column contains spaces — "iPhone SE (3rd generation)" — so it picked up "(3rd" and
# then queried a device that does not exist. `device info apps` returned nothing, and the script
# reported NOT INSTALLED about an app that was installed. **A confident wrong answer from a bad
# input**, which is the failure this whole harness exists to prevent.
if [ -z "$DEVICE" ]; then
	DEVJSON="$(mktemp)"
	xcrun devicectl list devices --json-output "$DEVJSON" >/dev/null 2>&1 || true
	DEVICE="$(python3 - "$DEVJSON" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
for x in d.get("result", {}).get("devices", []):
    print(x.get("identifier", ""))
    break
PY
)"
	rm -f "$DEVJSON"
fi
[ -n "$DEVICE" ] || { echo "no paired device found (xcrun devicectl list devices)" >&2; exit 1; }

mkdir -p "$OUT"
echo "== device: $DEVICE"

# ---- 1. IS IT ACTUALLY INSTALLED? -----------------------------------------------------------
#
# "COULD NOT ASK" AND "THE DEVICE SAID NO" ARE DIFFERENT ANSWERS and must not share an exit path.
# A disconnected or locked handset returns no app list, and reporting that as NOT INSTALLED sends
# somebody to rebuild and redeploy something that is already there.
echo "== installed apps, as the DEVICE reports them"
if ! APPS="$(xcrun devicectl device info apps --device "$DEVICE" 2>&1)"; then
	echo ""
	echo "CANNOT ASK THE DEVICE — the query failed. This is NOT a statement about whether the" >&2
	echo "app is installed; it means the handset did not answer. Is it connected and unlocked?" >&2
	echo "  xcrun devicectl list devices" >&2
	echo "$APPS" | tail -5 >&2
	exit 7
fi
echo "$APPS" | grep -iE "catacombs|yarl" || true
if ! echo "$APPS" | grep -qE "^[[:space:]]*[A-Za-z]"; then
	echo ""
	echo "CANNOT ASK THE DEVICE — it returned an empty app list, which no paired device does." >&2
	echo "Treating this as unanswered rather than as 'not installed'." >&2
	exit 7
fi
if ! echo "$APPS" | grep -q "$BUNDLE"; then
	echo ""
	echo "NOT INSTALLED: the device answered, and $BUNDLE is not among the apps it listed." >&2
	echo "An export exiting 0 is not a deployment. Run build_review_app.sh WITHOUT --no-install." >&2
	exit 3
fi
LINE="$(echo "$APPS" | grep "$BUNDLE" | head -1)"
echo ""
echo "== FOUND ON DEVICE: $LINE"

# ---- 2. LAUNCH IT, so it writes a fresh log -------------------------------------------------
echo "== launching $BUNDLE"
xcrun devicectl device process launch --device "$DEVICE" --terminate-existing "$BUNDLE" \
	> "$OUT/device-launch.log" 2>&1 || {
		tail -10 "$OUT/device-launch.log" >&2
		echo "launch failed — is the device unlocked?" >&2; exit 4; }
sleep 12    # let it boot, build the scene, and flush its first lines

# ---- 3. PULL THE APP'S OWN LOG --------------------------------------------------------------
# Diag writes to OS.GetUserDataDir(), which is Documents/ inside the app data container.
echo "== pulling Documents/diag.log"
rm -f "$OUT/DEVICE-tier1-boot.log"
xcrun devicectl device copy from --device "$DEVICE" \
	--domain-type appDataContainer --domain-identifier "$BUNDLE" \
	--source Documents/diag.log --destination "$OUT/DEVICE-tier1-boot.log" \
	> "$OUT/device-copy.log" 2>&1 || {
		tail -10 "$OUT/device-copy.log" >&2
		echo "log pull failed — the app may not have written one (is it a debug build?)" >&2
		exit 5; }

# ---- 4. WHAT THE LOG HAS TO SAY -------------------------------------------------------------
LOG="$OUT/DEVICE-tier1-boot.log"
echo ""
echo "== the three identifiers, from the handset"
grep -m1 "BUILD IDENTITY" "$LOG" || echo "  (no BUILD IDENTITY line — build predates the stamp)"
echo "  bundle (device): $BUNDLE"

fi   # end of the device interaction

echo ""
echo "== did it boot into the right scene, with the rig live?"
FAIL=0
check() {   # a name, and the pattern that proves it
	if grep -q "$2" "$LOG"; then
		echo "  OK    $1"
	else
		echo "  MISS  $1   (expected /$2/)"
		FAIL=1
	fi
}
# THE THEME CHECK USED TO NAME A DIRECTORY, AND THE DIRECTORY MOVED.
#
# It read `tile_theme_config=.*tier1_floors`, which was true when the tier-one family lived in
# `assets/tier1_floors/`. The course-aligned ashlar family lives in `assets/tier1_ashlar/`, so a
# correct build failed this check while the log plainly showed the right theme in force.
#
# The temptation is to widen the pattern until it passes. That is relaxing a test after reading a
# result, and it is the same error as deriving a plant's word list from a transcript. What follows
# is STRICTER than what it replaces, in two ways it could not manage before:
#
#   CONSISTENCY. The theme and the floor family must name the SAME directory. A hardcoded path
#   could never catch a build that laid one family's tiles under another family's theme — the
#   failure that actually costs a gate, because it looks entirely plausible.
#
#   THE FLOOR ACTUALLY LAID. `missing=0` and all three cross-checks green, ON THE HANDSET. The old
#   check could not see whether a single tile had been placed, let alone whether the engine
#   reproduced the composer's bond arithmetic, its material arithmetic and its finished pixels.
check "booted the review scene"        "corridor scene: tier1_floor_review"
check "incident overlays attached"     "floor overlays: cells="
check "rig panel constructed"          "\[Tier1\] rig:start:"
check "no losable state"               "losable-state check:"
check "floor family laid, every cross-check green" \
      "floor: laid=[1-9][0-9]* .*missing=0 .*edge_check=[0-9]*/OK stone_check=[0-9]*/OK paint_check=[0-9]*/OK"

# `|| true` ON BOTH, AND IT IS NOT DECORATION. Under `set -euo pipefail` a grep that matches
# nothing fails, and a failing command substitution ABORTS THE SCRIPT — so the single likeliest
# real failure, the floor never being laid at all, exited 1 with a bare shell error instead of
# reporting NOT VERIFIED. An abort and a verdict are different things, which is the same
# distinction this script already draws between "could not ask the device" and "the device said
# no". Caught by the failability test, not by reading the code.
THEME_DIR="$(grep -o 'tile_theme_config=res://[^ ]*' "$LOG" 2>/dev/null | head -1 \
	| sed 's#.*/assets/\([^/]*\)/.*#\1#' || true)"
FAMILY_DIR="$(grep -o 'floor: laid=.*manifest=res://[^ ]*' "$LOG" 2>/dev/null | head -1 \
	| sed 's#.*/assets/\([^/]*\)/.*#\1#' || true)"
if [ -n "$THEME_DIR" ] && [ "$THEME_DIR" = "$FAMILY_DIR" ]; then
	echo "  OK    theme and floor family agree   ($THEME_DIR)"
else
	echo "  MISS  theme and floor family disagree   (theme=${THEME_DIR:-none} family=${FAMILY_DIR:-none})"
	echo "        A build laying one family's tiles under another family's theme looks entirely"
	echo "        plausible in a screenshot. That is why this is checked and not assumed."
	FAIL=1
fi

echo ""
grep -m1 "floor overlays: cells=" "$LOG" | sed 's/^/  /' || true
grep -m1 "light rig:" "$LOG" | sed 's/^/  /' || true

echo ""
if [ "$FAIL" = "0" ]; then
	echo "VERIFIED ON DEVICE — installed, launched, booted into tier1_floor_review, rig live."
	echo "log: ${LOG#$ROOT/}"
else
	echo "NOT VERIFIED — the app is installed but did not report what it should have." >&2
	echo "log: ${LOG#$ROOT/}" >&2
	exit 6
fi
