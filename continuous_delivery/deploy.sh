#!/bin/bash

continuous_delivery/build.sh

$GAE_SDK/appcfg.py update build --oauth2 --noauth_local_webserver

$GAE_SDK/appcfg.py set_default_version build --email=renzon@gmail.com --oauth2 --noauth_local_webserver
