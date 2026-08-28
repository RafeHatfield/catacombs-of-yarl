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

while [ $# -gt 0 ]; do
	case "$1" in
		--device) DEVICE="$2"; shift 2 ;;
		--bundle) BUNDLE="$2"; shift 2 ;;
		--out)    OUT="$2"; shift 2 ;;
		*) echo "unknown arg: $1" >&2; exit 2 ;;
	esac
done

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
check "booted the review scene"        "corridor scene: tier1_floor_review"
check "tier-one floor theme in force"  "tile_theme_config=.*tier1_floors"
check "incident overlays attached"     "floor overlays: cells="
check "rig panel constructed"          "\[Tier1\] rig:start:"
check "no losable state"               "losable-state check:"

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
