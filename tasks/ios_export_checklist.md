# iOS Export Quick Reference

## Pre-flight (one-time setup, already done)
- [x] Xcode with Apple account signed in
- [x] iPhone paired and Developer Mode enabled
- [x] Godot export templates downloaded
- [x] Export preset configured with Team ID + bundle identifier

## Every Export
1. In Godot: `Project > Export`
2. Select iOS preset
3. **Options tab**: verify "Export Project Only" is **ON**
4. **Resources tab**: verify "*.yaml" in non-resource filter
5. Click "Export Project..." → save to `~/development/yarl-export/`
6. Godot will say "Failed" — this is expected (xcodebuild skip). Click OK.
7. Open `~/development/yarl-export/yarl.xcodeproj` in Xcode
8. Signing & Capabilities → Team → Personal Team (if not already set)
9. Select your iPhone from device dropdown
10. Hit Run

## If you get "Undefined symbol: _main"
- You forgot to check "Export Project Only" in step 3
- Clean: `rm -rf ~/development/yarl-export/*`
- Re-export with the checkbox ON

## If you get "Developer App Certificate not trusted"
- On iPhone: Settings > General > VPN & Device Management > Trust
- If stuck: restart iPhone

## Adding new YAML types
- Add factory entry to `src/Logic/Content/AotObjectFactory.cs`
- Add any new collection types (Dictionary<string, List<T>>, etc.)

## Adding new UI buttons
- Use `TouchButton` (not Godot `Button`) — Godot buttons have offset hit areas on iOS
- Pattern: `new TouchButton { Text = "...", Pressed += () => ... }`
