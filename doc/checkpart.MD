# checkpart
The checkpart subcommand is meant for integrity-checking build-part versioning. When a build-part is to be used to create a deployment artifact,
or to do a direct build/deploy combo, all parts of this build should be frozen. And by default, frozen versions of the build-parts
shall be used when building the artifact.

A frozen build-part version consists of:
* A main.json or main-XXXXXX.json file that should now be considered immutable, as should any closure files referenced from the main.json.
* An entry in the *lockfile* of the build-part containing:
  - A hash of the main.json and referenced clojure files.
  - A dependencies snapshot for the build-part version.
  
The checkpart subcommand will:
* Calculate the hashes of all version related transaction and clojure file and files in a build-part 
* Compare the hashes to those in the build-part lockfile

The checkpart command has one positional argument.

* part: The name of the build-part to check.

The main optional arguments are:

* --dir : The top level build directory of the [fsst build target](buildtarget.MD) tree.
