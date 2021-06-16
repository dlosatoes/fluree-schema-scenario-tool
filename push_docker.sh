#!/bin/bash
docker push pibara/fsst:stable
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-stable
docker push pibara/fsst:`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
echo docker push pibara/fsst:beta
echo docker push pibara/fsst:`python3 git_info_fluree_latest.py | sed -e 's/\r//'`
echo docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`python3 git_info_fluree_latest.py | sed -e 's/\r//'`
docker push pibara/fsst:alpha
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-alpha
docker push pibara/fsst:fluree-snapshot-`date --iso-8601`|sed  -e 's/\r//'
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-fluree-snapshot-`date --iso-8601`|sed  -e 's/\r//'
