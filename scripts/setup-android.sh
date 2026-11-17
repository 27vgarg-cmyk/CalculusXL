#!/usr/bin/env bash
# Downloads the Android SDK, emulator and an Android 11 (API 30) phone image (~3 GB total),
# then creates a virtual phone called "gamephone".
# API 30 x86_64 images include Google's ARM->x86 translation, so most ARM-only games can still install.
set -e
SDK=${ANDROID_HOME:-$HOME/android-sdk}
IMG="system-images;android-30;google_apis;x86_64"

if [ ! -e /dev/kvm ]; then
  echo "!! /dev/kvm not found. The emulator will NOT be able to run on this machine."
  echo "!! Downloading 3 GB is pointless here. See README: 'Why APKs might not work'."
  read -p "Continue anyway? [y/N] " a; [ "$a" = "y" ] || exit 1
fi

mkdir -p "$SDK/cmdline-tools"
if [ ! -x "$SDK/cmdline-tools/latest/bin/sdkmanager" ]; then
  echo "Downloading Android command-line tools..."
  curl -L -o /tmp/cmdtools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
  rm -rf "$SDK/cmdline-tools/latest" /tmp/cmdtools && unzip -q /tmp/cmdtools.zip -d /tmp/cmdtools
  mv /tmp/cmdtools/cmdline-tools "$SDK/cmdline-tools/latest"
fi
export PATH="$SDK/cmdline-tools/latest/bin:$SDK/platform-tools:$SDK/emulator:$PATH"

yes | sdkmanager --sdk_root="$SDK" --licenses >/dev/null
sdkmanager --sdk_root="$SDK" "platform-tools" "emulator" "build-tools;34.0.0" "$IMG"

echo no | avdmanager create avd -n gamephone -k "$IMG" -d pixel --force
CFG="$HOME/.android/avd/gamephone.avd/config.ini"
cat >> "$CFG" <<CONF
hw.ramSize=3072
disk.dataPartition.size=6G
hw.keyboard=yes
hw.gpu.enabled=yes
hw.gpu.mode=swiftshader_indirect
hw.lcd.width=720
hw.lcd.height=1280
hw.lcd.density=320
CONF
echo ""
echo "Android setup done. Now run: ./start-apk.sh"
