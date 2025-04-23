#!/bin/bash
apt-get update && \
apt-get install -y wget gnupg && \
wget -qO- https://deb.nodesource.com/setup_18.x | bash - && \
apt-get install -y nodejs && \
npm i -g playwright && \
npx playwright install
