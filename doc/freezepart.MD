# freezepart
The freezepart subcommand is meant for build-part versioning. When a build-part is to be used to create a deployment artifact,
or to do a direct build/deploy combo, all parts of this build should be frozen.And by default, frozen versions of the build-parts
shall be used when building the artifact.

A frozen build-part version consists of:
* A main.json or main-XXXXXX.json file that should now be considered immutable, as should any closure files referenced from the main.json.
* An entry in the *lockfile* of the build-part containing:
  - A hash of the main.json and referenced clojure files.
  - A dependencies snapshot for the build-part version.
  
The freezepart subcommand will:
* Add a new version entry to the lockfile.
* Create a new zero-transactions main-XXXXXX.json file.
* If needed, migrate from a single-file build-part to a directory build-part.

The freezepart command has one positional argument.

* part: The name of the build-part to freeze.

The main optional arguments are:

* --dir : The top level build directory of the [fsst build target](buildtarget.MD) tree.
