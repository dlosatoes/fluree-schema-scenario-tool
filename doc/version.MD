# version

The *version* sub command serves litle purpose of its own, but for troubleshooting.
The docker related sub-commands [dockertest](dockertest.MD) and [dockerdeploy](dockerdeploy.MD) rely on cooperation between the *fsst* version on the host system and the one on the invoked docker image. For this purpose, the *version* subcommand exists. If the two *fsst* tools have roughly the same version, for example 0.2.2 and 0.2.5, there should be no wories about the correct workings. If however the image has version 0.1.x and the host system has 0.2.5, the docker related sub commands that require cooperation between the host and the docker image version of the fsst tool will not work. 

The *version* subcommand only displays the version of the invoked fsst tool. To compare versions, use the [versioncheck](versioncheck.MD) command instead.

For use in a [CICD](gitlabci.MD) setup, it is suggested to always include an invokation of this subcommand for debugging purposes.

```bash
./ffst version
```
