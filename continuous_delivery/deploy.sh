#!/bin/bash

continuous_delivery/build.sh

$GAE_SDK/appcfg.py update build --email=renzon@gmail.com --oauth2

$GAE_SDK/appcfg.py set_default_version build --email=renzon@gmail.com --oauth2
