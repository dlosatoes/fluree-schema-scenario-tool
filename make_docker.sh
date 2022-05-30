#!/bin/bash
#echo "Making from downloaded stable"
#docker build --no-cache -t pibara/fsst:stable .
#echo -n STABLE = 
#docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'
#docker tag pibara/fsst:stable pibara/fsst:`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
#docker tag pibara/fsst:stable pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`
#docker tag pibara/fsst:stable pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-stable
#docker tag pibara/fsst:stable pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
#echo
echo "Making latest beta/stable from github"
echo -n BETA =
python3 git_info_fluree_latest.py
docker build --no-cache -t pibara/fsst:beta . -f Dockerfile-latest-github
docker tag pibara/fsst:beta pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-beta
docker tag pibara/fsst:beta pibara/fsst:`python3 git_info_fluree_latest.py | sed -e 's/\r//'` 
docker tag pibara/fsst:beta pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`python3 git_info_fluree_latest.py | sed -e 's/\r//'`
docker tag pibara/fsst:beta pibara/fsst:stable
docker tag pibara/fsst:beta pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-stable
echo "Making latest alpha from github"
echo -n BETA =
python3 git_info_fluree_latest_alpha.py
docker build --no-cache -t pibara/fsst:alpha . -f Dockerfile-alpha-github
docker tag pibara/fsst:beta pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-alpha
docker tag pibara/fsst:beta pibara/fsst:`python3 git_info_fluree_latest_alpha.py | sed -e 's/\r//'`
docker tag pibara/fsst:beta pibara/fsst:v`grep "VERSION.*=" fsst | sed -e 's/.*= *"//' -e 's/"//'`-`python3 git_info_fluree_latest_alpha.py | sed -e 's/\r//'`

