# artifactdeploy

The *artifactdeploy* subcommand is meant for deploying a pre-build FlureeQL atrifact file to a running FlureeDB server. This artifact file is a JSON file that can be created by hand, or using the [artifact](artifact.MD) subcommand.

The artifactdeploy command has two positional comandline arguments:

* input : The filename or path of the FlureeQL artifact file to deploy.
* db : The name of the database to create and to deploy the transactions in the artifact file to.

```bash
./fsst artifactdeploy artifact.json test/mydb
```

Like the [deploy](deploy.MD) and the [test](test.MD) subcommands, the artifactdeploy subcommand has the optional *--host* and *--port* arguments (defaulting to *localhost* and *8090*) that can be used to designate a FlureeDB host.

```bash
./fsst artifactdeploy artifact.json test/mydb --host otherhost --port 17080
```

Also like the [deploy](deploy.MD) and the [test](test.MD) subcommands, the *artifactdeploy* subcommand uses signed operations against the FlureeDb *command* API endpoint, and for this requires an ECDSA signing to perform its operations.  To provide this key, there are three optional arguments.

## --dockerfind <tag>

If you used the [dockerstart](dockerstart.MD) command to start a *fsst* FlureeDB docker container on your local system, you can use --dockerfind to specify that *artifactdeploy* should try and find the docker container and from this docker container, extract the signing key. A *tag* designates the FlureeDB version to use. You can download different tagged versions of the *fsst/FlureeDB* docker image from [dockerhub](https://hub.docker.com/r/pibara/fsst/tags?page=1&ordering=last_updated). 

If none of the tree key related arguments (--dockerfind, --createkey. --keyfile) is specified, --dockerfind with the tag *beta* is implied.

```bash
./fsst artifactdeploy artifact.json test/mydb --dockerfind fluree-snapshot-20201213
```

## --keyfile <file>

If instead of a docker container with FlureeDB, you are using a local install of FlureeDB, it can be usefull to designate the key file containing the default signing key with this option.

```
./fsst artifactdeploy artifact.json test/mydb --keyfile fluree-0.15.7/default-private-key.txt
```

## --createkey <key>

The third way to supply the command with a signing key is to supply the yey itself on the commandline using the --createkey option.

```bash
./fsst artifactdeploy artifact.json test/mydb --createkey d7ecd0776898eb4cb8c064fffa62d91988a2a2233ba74de8649349c246fb7996
```

