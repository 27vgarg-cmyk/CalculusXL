#!/usr/bin/env bash
# Boots the "gamephone" emulator onto virtual display :2 (streamed on port 6081).
SDK=${ANDROID_HOME:-$HOME/android-sdk}
export PATH="$SDK/platform-tools:$SDK/emulator:$PATH"
[ -e /dev/kvm ] && [ ! -w /dev/kvm ] && sudo chmod 666 /dev/kvm
DISPLAY=:2 emulator -avd gamephone -gpu swiftshader_indirect -no-audio -no-boot-anim \
  -no-snapshot-save -no-metrics -accel on >/tmp/emulator.log 2>&1 &
adb wait-for-device
until [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do sleep 3; done
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
echo "Emulator booted"
