#!/bin/bash

sudo  raspivid -t 0 -w 160 -h 120 -o - | /usr/local/bin/ffmpeg -i - -f mpeg1video http://remotevision.herokuapp.com/love/160/120/
