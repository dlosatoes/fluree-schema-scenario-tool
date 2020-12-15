# dockertest

The *dockertest* subcommand has the same function as the [test](test.MD) subcommand, but other than *test*, an *fsst* docker image is spinned up (with a mounted project dir), FlureeDB is started within that docker container, and the test is run within the container.

This is very usefull when we want to test our project against multiple FlureeDB versions, but it does come at a price. It can take a bit of time for the docker container and FlureeDB to spin up before the test is run.

The dockertest command only has optional commandline parameters, but chances are you will want to specify a few. The options --dir, --target and --verboseerrors work exactly as they do for the [test](test.MD) subcommand. 

The --tag option specifies which tagged version of the pibara/fsst should be used as docker container.

```bash
./fsst dockertest --dir experiments --target user_ok --tag stable
```

### --linger

If after running the tests, you want to have a look at the database, use the --linger option. This option will keep the container running and will expose the FlureeDB WUI on port 8090 on localhost

```bash
./fsst dockertest --dir experiments --target user_ok --tag stable
```
A web browser tab will get opened when the tests are done.

### --verbosefluree

If you wish to see exactly what fluree is doing during the test, you can specify this option in order to get all fluree logs on standard output.
