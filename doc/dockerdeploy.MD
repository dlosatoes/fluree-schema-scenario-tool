# dockerdeploy

The *dockerdeploy* subcommand has the same function as the [deploy](deploy.MD) subcommand, but other than *deploy*, an *fsst* docker image is spinned up (with a mounted project dir), FlureeDB is started within that docker container, and the deploy is run within the container.

It is important to note that there is no persistance with a deploy ran like this. When the container is stopped, your database will be gone. Usually for testing and development this is what you want.

The dockerdeploy command has one positional argument:

* db: Name for the new database to deploy to.

The optional --tag option specifies which tag of the pibara/fsst docker image you want to deploy to.  The --dir, --target and --verboseerrors options work exactly as the same arguments work for [deploy](deploy.MD).

```bash
./fsst dockerdeploy test/mydb --dir experiments --target user_ok --tag stable --verbosefluree
```


One option worth mentioning is the --deamonize. That option detaches from the docker container and keeps it running in the background.

```bash
./fsst dockerdeploy test/mydb --dir experiments --target user_ok --tag stable --daemonize
```

