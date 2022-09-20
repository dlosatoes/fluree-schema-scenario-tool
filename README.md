## Fluree Schema Scenario Tool

This project contains a simple yet usefull tool for database schema development for FlureeDB.
Note that there have been major updates to the commandline interface from the 0.1 version of this tool. Please upgrade both the tool and the accompanying [docker images](https://hub.docker.com/r/pibara/fsst/tags?page=1&ordering=last_updated) if you are currently using the 0.1 version.

From the 0.2 version of *fsst*, the command line has a number of sub commands.
The following sub-commands run without docker and without a local FlureeDB server.

* [version](doc/version.MD) : Print the *fsst* version
* [artifact](doc/artifact.MD) : Compile a single file FlureeDB schema from a [build target](doc/buildtarget.MD).

The following sub-commands can run without docker, but need a FlureeDB server to communicate with

* [artifactdeploy](doc/artifactdeploy.MD) : Create a FlureeDB database and deploy the transactions in the artifact file to it.
* [deploy](doc/deploy.MD) : Compile FlureeDB schema from a [build target](doc/buildtarget.MD) and deploy it to FlureeDB.
* [test](doc/test.MD) : Run all unit tests for a [build target](doc/buildtarget.MD)

If you have Docker installed, the following commands should also be available

* [versioncheck](doc/versioncheck.MD) : Compare the version of the fsst tool on the host with the one on the guest docker for compatibility.
* [dockerstart](doc/dockerstart.MD) : Start a FlureeDB version in a docker container.
* [dockerstop](doc/dockerstop.MD) : Stop docker container running given FlureeDB version.
* [dockerparams](doc/dockerparams.MD) : Retreive base info from a running docker container running a given FlureeDB version.
* [dockerdeploy](doc/dockerdeploy.MD): Start an *fsst* docker container and compile and deploy a FlureeDB schema from a [build target](buildtarget.MD), from within the container.
* [dockertest](doc/dockertest.MD): Start an *fsst* docker container and run all unit tests for a [build target](buildtarget.MD) from within the container.

### Install

The easiers way to install fsst is the use of pip. There are four ways to install fsst.

#### full install

This should be the default as it enables all the subcommands you might want with full functionality.

```sh
python3 -m pip install 'fsst[docker,domainapi]'
```
####

#### Without the domain API

```sh
python3 -m pip install 'fsst[docker]'
```

#### Without support for docker sub commands

```sh
python3 -m pip install 'fsst[domainapi]'
```

### Minimal

```sh
python3 -m pip install fsst
```
### Gitlab CICD

For usage in a gitlab CICD pipeline, chack out [this page](doc/gitlabci.MD)
