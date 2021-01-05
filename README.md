## Fluree Schema Scenario Tool

This project contains a simple yet usefull tool for database schema development for FlureeDB.
Note that there have been major updates to the commandline interface from the 0.1 version of this tool. Please upgrade both the tool and the accompanying [docker images](https://hub.docker.com/r/pibara/fsst/tags?page=1&ordering=last_updated) if you are currently using the 0.1 version.

From the 0.2 version of *fsst*, the command line has a number of sub commands.
The following sub-commands run without docker and without a local FlureeDB server.

* [version](doc/version.MD) : Print the *fsst* version
* [artifact](doc/artifact.MD) : Compile a single file FlureeDB schema from a [build target](doc/buildtarget.MD).
* [freezepart](doc/freezepart.MD): Freeze a given build-part and its dependencies and create an empty new version.
* [checkpart](doc/checkpart.MD): Check the integrity of the frozen components of a build-part.
* [unfreezedeps](doc/unfreezedeps.MD): Unfreeze the dependencies of a build-part; use with care.
* [refreezedeps](doc/refreezedeps.MD): Refreeze the unfrozen dependencies of a build-part.
* [freezetarget](doc/freezetarget.MD): Freeze a build target and create a new empty future version.

The following sub-commands can run without docker, but need a FlureeDB server to communicate with

* [artifactdeploy](doc/artifactdeploy.MD) : Create a FlureeDB database and deploy the transactions in the artifact file to it.
* [artifactupgrade](doc/artifactupgrade.MD) : Do a smart upgrade using database stored upgrade info.
* [deploy](doc/deploy.MD) : Compile FlureeDB schema from a [build target](doc/buildtarget.MD) and deploy it to FlureeDB.
* [test](doc/test.MD) : Run all unit tests for a [build target](doc/buildtarget.MD)

If you have Docker installed, the following commands should also be available

* [versioncheck](doc/versioncheck.MD) : Compare the version of the fsst tool on the host with the one on the guest docker for compatibility.
* [dockerstart](doc/dockerstart.MD) : Start a FlureeDB version in a docker container.
* [dockerstop](doc/dockerstop.MD) : Stop docker container running given FlureeDB version.
* [dockerparams](doc/dockerparams.MD) : Retreive base info from a running docker container running a given FlureeDB version.
* [dockerdeploy](doc/dockerdeploy.MD): Start an *fsst* docker container and compile and deploy a FlureeDB schema from a [build target](doc/buildtarget.MD), from within the container.
* [dockertest](doc/dockertest.MD): Start an *fsst* docker container and run all unit tests for a [build target](doc/buildtarget.MD) from within the container.

### Dependencies

Prior to using the *fsst* tool, use *pip install* to install all dependencies.
Note that these dependencies should not be needed if you only intent to use the unit-test (using docker) or the docker temp instance of Fluree.

```bash
python3 -m pip install base58 aioflureedb bitcoinlib docker PyYAML
```
On windows you need also need this to make bitcoinlib work:
```powershell
pip install sqlalchemy --upgrade
```
this will result in an error:
```
ERROR: bitcoinlib 0.5.1 has requirement SQLAlchemy==1.3.2, but you'll have sqlalchemy 1.3.20 which is incompatible.
```
But fsst will work despite the error.

It is important to note that as some dependencies are only needed for some subcommands, it is possible to run *fsst* without some of the dependencies installed, but doing so will disable several subcommands.

If you plan to use the docker related sub commands, you should also fetch the relevant docker images from dockerhub. These are docker files containing both a version of FlureeDB and the latest version of the *fsst* tool.

```bash
docker pull pibara/fsst:stable
docker pull pibara/fsst:beta
docker pull pibara/fsst:alpha
```

### Gitlab CICD

For usage in a gitlab CICD pipeline, chack out [this page](doc/gitlabci.MD)
