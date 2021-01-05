# unfreezedeps
The unfreezedeps subcommand is meant for build-part versioning. When a build-part is to be used to create a deployment artifact,
or to do a direct build/deploy combo, all parts of this build should be frozen.And by default, frozen versions of the build-parts
shall be used when building the artifact.

A frozen build-part version consists of:
* A main.json or main-XXXXXX.json file that should now be considered immutable, as should any closure files referenced from the main.json.
* An entry in the *lockfile* of the build-part containing:
  - A hash of the main.json and referenced clojure files.
  - A dependencies snapshot for the build-part version.

In most circumstances, a frozen version will never need to be unfrozen. There is a possible and realistic scenario though where a 
partial unfreeze and refreeze of a frozen version could be warranted. 

Let's now look at the scenario where an unfreeze and refreeze would absolutely be called for.

Build-part Z is frozen, and is unchanged, but build-part-X is split into two, build-part-X and build-part-Y, 
because splitting it up makes sense for one of the build-targets.
So now version 1 of build-part-Z that is frozen has a frozen dependency on build-part-X that doesn't specify a version. 
If a build-target containing version 1 of build-part-Z would get build, gets build with a new version of build-part-X 
and the new build-part-Y, the needed dependency from build-part-Z on build-part-Y won't be known to the build system, and
built-part-Z may get transacted before the required build-part-Y has been transacted.

What is needed is the posibility to add a conditional dependency to an already frozen build-part version. 

We need to go from the unary dependency:

* Any version of build-part-X

To:

* Version 1 of build-part-X
* Any version greater than 1 of build-part-X combened with any version of build-part-Y

Invoking the unfreezedeps command allows for this to be done.

Note that editing already frozen versions is not competely without risk. Care should be taken to make sure
that old version builds shall still result in the same outcomes. 

The unfreezedeps command has one positional argument.

* part: The name of the build-part to freeze.

The main optional arguments are:

* --dir : The top level build directory of the [fsst build target](buildtarget.MD) tree.
