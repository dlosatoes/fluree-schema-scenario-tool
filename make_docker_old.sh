#!/bin/bash
docker build -t pibara/fsst:stable .
docker build -t pibara/fsst:beta . -f Dockerfile-latest
docker build --no-cache -t pibara/fsst:fluree-master . -f Dockerfile-fluree-master
echo -n STABLE = 
docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'
docker tag pibara/fsst:stable pibara/fsst:`docker run -it pibara/fsst:stable find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
echo -n BETA = 
docker run -it pibara/fsst:beta find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'
docker tag pibara/fsst:beta pibara/fsst:`docker run -it pibara/fsst:beta find /usr/src -type d|grep fluree|sed -e 's/.*\///' -e 's/\r//'`
