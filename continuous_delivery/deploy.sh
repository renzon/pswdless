#!/bin/bash
continuous_delivery/build.sh

$GAE_SDK/appcfg.py update build --email=$BOT_EMAIL --passin <<<"$BOT_PASSWORD"

$GAE_SDK/appcfg.py set_default_version build --email=$BOT_EMAIL --passin <<<"$BOT_PASSWORD"
