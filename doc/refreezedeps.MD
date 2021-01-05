# refreezedeps
The unfreezedeps subcommand is meant for build-part versioning. It does the opposite from [unfreezedeps](unfreezedeps.MD). 

Opposit to [unfreezedeps](unfreezedeps.MD), the *refreezedeps* sub-command will:

The *unfreezedeps* command will:

* Extract dependency info from the edited *unfrozen_deps.yml* file that was originally created by [unfreezedeps](unfreezedeps.MD).
* Write the relevant parts of the above info to the proper versions inside of the the build-part lockfile
* Write the relevant part of the above info to the build-part level build.yml file

The refreezedeps command has one positional argument.

* part: The name of the build-part to freeze.

The main optional arguments are:

* --dir : The top level build directory of the [fsst build target](buildtarget.MD) tree.
