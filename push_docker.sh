#!/bin/bash
echo Pushing stable
docker push pibara/fsst:stable
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-stable
docker push pibara/fsst:`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
echo Pushing beta
docker push pibara/fsst:beta
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-beta
docker push pibara/fsst:`python3 git_info_fluree_latest.py | sed -e 's/\r//'`
docker push pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`python3 git_info_fluree_latest.py | sed -e 's/\r//'`
