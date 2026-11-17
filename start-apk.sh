#!/usr/bin/env bash
# APK Runner: UI on port 8081, phone screen on port 6081
cd "$(dirname "$0")"
bash scripts/start-display.sh 2 5902 6081 900x1400
echo ""
if [ ! -e /dev/kvm ]; then
  echo "  WARNING: no /dev/kvm -> the Android emulator cannot run on this machine."
  echo "  The website will still open and explain this. See README."
else
  [ -w /dev/kvm ] || sudo chmod 666 /dev/kvm
  [ -d "${ANDROID_HOME:-$HOME/android-sdk}/emulator" ] || echo "  Android SDK missing -> run: bash scripts/setup-android.sh"
fi
echo "  APK Runner is up. Open the PORTS tab and click the globe on port 8081."
echo ""
exec python3 apk-runner/app.py
