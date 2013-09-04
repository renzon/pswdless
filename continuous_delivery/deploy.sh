#!/bin/bash

continuous_delivery/build.sh

$GAE_SDK/appcfg.py update build --oauth2

$GAE_SDK/appcfg.py set_default_version build --oauth2
