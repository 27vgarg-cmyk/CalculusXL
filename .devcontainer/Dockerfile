FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04
ENV DEBIAN_FRONTEND=noninteractive
# Wine (32+64 bit) for .exe, a virtual screen + browser streaming, Java for the Android SDK tools
RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y --no-install-recommends \
      wine wine64 wine32:i386 \
      xvfb x11vnc novnc websockify fluxbox xdotool \
      fonts-dejavu fonts-liberation \
      python3 python3-flask \
      openjdk-17-jre-headless unzip curl ca-certificates \
      libpulse0 libgl1 libnss3 libxcomposite1 libxcursor1 libxi6 libxtst6 libxdamage1 libxkbfile1 \
    && rm -rf /var/lib/apt/lists/*
ENV ANDROID_HOME=/home/vscode/android-sdk
