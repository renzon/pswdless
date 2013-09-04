#!/bin/bash

continuous_delivery/build.sh

appcfg.py update build --email=renzon@gmail.com --oauth2

appcfg.py set_default_version build --email=renzon@gmail.com --oauth2
