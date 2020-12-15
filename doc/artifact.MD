# artifact

The *artifact* subcommand is meant for building a FlureeQL JSON artifact file from an [fsst build target](buildtarget.MD). 

The artifact command has one positional argument.

* output : The filename or path of the FlureeQL artifact file to compile from the build target specification.

The main optional arguments are:

* --dir : The top level build directory of the [fsst build target](buildtarget.MD) tree.
* --target : The target as defined in build.json (found in the dir specified by --dir)

The --dir argument defaults to the name "fluree_parts". --target defaults to the "default" target.

```
./fsst artifact artifact.json --dir experiments --target user_ok
```

## --verboseerrors

The --verboseerrors argument is a binary flag. If set, the building of the [fsst build target](buildtarget.MD) will apply an extra bit of processing on the processed operations in transactions performed on the **_rule** collection.

While in production it can be usefull to have access controll errors be a bit ambiguous from a security perspective, during testing and development, it can be important to know what rule is failing. For this purpose, the --verboseerrors flag will trigger a patch of all *_role* transaction operations without a defined error message.

```
./fsst artifact artifact.json --dir experiments --target user_ok --verboseerrors
```
