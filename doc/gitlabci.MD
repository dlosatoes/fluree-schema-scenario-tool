## Using fssf in a gitlab CICD pipeline

This page describes the use of the *fsst* tool in a gitlab CICD pipeline. This info is currently not fully complete.

Let's say we have a gitlab repository with the fsst build directory in the subdir *fluree_parts*, and a file *.gitlab-ci.yml* YAML file containing the CICD setup for the project. Let's also say our target is named *latest".

We will be needing at least two stages.

```yaml
stages:
  - test latest
  - latest artifact

```

Now for our first CICD stage, *test latest*, we need to create a little job.

```yaml
fsstcheckalpha:
  stage: test latest
  image: pibara/fsst:alpha
  script:
    - /usr/src/fsst/ffst version
    - ln -s `pwd`/fluree_parts /usr/src/fsst/fluree_parts
    - cd /usr/src/fsst/
    - /usr/src/fsst/fsst guesttest --target latest --network pipeline --verboseerrors
  only:
    changes:
      - fluree_parts/**.json
      - fluree_parts/**.clj
  allow_failure: false
```

Notice, for this job we use the *alpha* version of the fsst docker image. This job is only run if a JSON or Clojure file in the build dir is added or updated. Now lets look at the script.

First, for debugging purposes, we print the version of fsst.

Secondly, as we are running in a pipeline, we aren't in the usual working directory yet, but in an injected directory containing the project tree, including the *fluree_parts* dir that is our build tree dir. What we need to do is symlink the build dir from the regular docker working dir.

Finaly we jump to the docker working dir and start fsst in *guesttest* mode. In this mode, fsst will start flureedb and will wait for a file holding the default signing key to appear before it comences its operations. 

This stage will act as sentry for the other stages. If this stage fails because a test fails, the pipeline gets aborted.

For the next stage, we create a much simpler job:

```yaml
fsstbuild:
  stage: latest artifact
  image: pibara/fsst:alpha
  script:
    - /usr/src/fsst/ffst version
    - /usr/src/fsst/fsst artifact schema-latest.json --verboseerrors --target latest
  only:
    refs:
      - master
    changes:
      - fluree_parts/**.json
      - fluree_parts/**.clj
  artifacts:
    paths:
      - schema-latest.json
  allow_failure: false
```

Much is the same as the previous job, lets discuss the differences. In this job we create an artifact *schema-latest.json* on success. The script for doing so is a simple one-liner, invoking the [fsst artifact subcommand](artifact.MD)

Now in a later stage shis artifact could get deployed using for example the [fsst artifactdeploy subcommand](artifactdeploy.MD). Though as this later stage depends heavily on the deployment platform and environment, a discussion of that stage falls outside of the scope of this doc.
