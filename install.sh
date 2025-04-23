#!/bin/bash
apt-get update
apt-get install -y wget gnupg software-properties-common
npx playwright install --with-deps
