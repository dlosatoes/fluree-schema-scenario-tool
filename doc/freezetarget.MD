# freezetarget
The freezetarget subcommand is meant for build-target versioning. When a build-target is to be used to create a deployment artifact,
or to do a direct build/deploy combo, as a prerequisite, all build-parts of this build should be frozen. And by default, frozen versions of the build-parts
shall be used when building the artifact.

A frozen build-target version consists of:
* A single latest-version sub-section in the build-target section of the top-level build.yml
* A *targetlock-\<target>.json* file containing:
  * a frozen version of all preceding versions info from build.yml, also containing actual sequence information from the moment of freeze.
  * A list of *latest* versions for each of the build-parts at time of freeze.

  
The freezetarget subcommand will:
* Move build.yml versions to the lockfile and leave the target section of the build.yml file with just one (new) entry 
* Calculate and add sequence info to the lockfile for each moved section.
* Record latest version for build-parts in the lockfile.

The main optional arguments are:

* --dir : The top level build directory of the [fsst build target](buildtarget.MD) tree.
* --target: FlureeDB, build target as defined in build.json ('default' if undefined)
* --verbosebuildfile: Don't use the diff-only version of the build.yml format, be verbose.
