# version

The docker related sub-commands [dockertest](dockertest.MD) and [dockerdeploy](dockerdeploy.MD) rely on cooperation between the *fsst* version on the host system and the one on the invoked docker image. For this purpose, the *versioncheck* subcommand exists. If the two *fsst* tools have roughly the same version, for example 0.2.2 and 0.2.5, there should be no wories about the correct workings. If however the image has version 0.1.x and the host system has 0.2.5, the docker related sub commands that require cooperation between the host and the docker image version of the fsst tool will not work. 

The *versioncheck* subcommand compares the version inside of a given tagged version of the fsst docker image to the one on the host system.

The versioncheck subcommand has a single optional commandline argument:

* --tag : The tag of the pibara/fsst docker image to check.

If --tag isn't specified, *beta* is assumed.

Check [dockerhub](https://hub.docker.com/r/pibara/fsst/tags?page=1&ordering=last_updated) for available tags.

```bash
./ffst versioncheck --tag alpha
```
