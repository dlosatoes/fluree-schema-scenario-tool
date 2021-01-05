import sys
import os
import json
try:
    import aioflureedb
except ModuleNotFoundError:
    pass

from fsst.expand_utils import expand_operation, expand_transaction
from fsst.tests import smartfunction_test
from fsst.filldb import filldb

async def fluree_main(notest, network, host, port, output, createkey, createid,
                      target, fluree_parts, verboseerrors):
    # pylint: disable=too-many-branches, too-many-statements
    # TODO: We may want to dismantle this function and refactor. Below is a remnant
    #       of the 0.1 version of fsst that didn't yet use subcommands.
    """The tools main function

    Parameters
    ----------
    notest: boolean
        Boolean indicating not to run tests, but to still deploy compiled transactions to db
    network: string
        Fluree network name for all databases to create and test with.
    host: string
        The FlureeDB host
    port: int
        The TCP port of the FlureeDB host
    output: string
        File path for output artifact
    createkey: string
        The ECDSA signing key for our transactions. This should be the host default key.
    createid: string
        The key-id of the above signing key
    target:
        The build target name to use.
    fluree_parts: string
        Fluree build sources top dir directory path
    verboseerrors: boolean
        Add extra error strings to rules if undefined.
    """
    # pylint: disable=too-many-locals,too-many-arguments
    maxblock = [expand_operation({
        "_id": "_fn$lastblock",
        "name" : "lastBlock",
        "doc" : "Get the number of the last known block on the ledger",
        "code_from_query": {
           "select": "?maxBlock",
           "where": [
               ["?s", "_block/number", "?bNum"],
               ["?maxBlock",  "#(max ?bNum)"],
               ["?s", "_block/number", "?maxBlock"]
           ]
        }
    },".",fluree_parts,False)[0]]
    try:
        expanded = list()
        expanded.append(maxblock)
        # Build.json contains the different build targets and lists their components.
        # Fetch the specified target from this file.
        try:
            with open(fluree_parts + "/build.json") as buildfile:
                build = json.load(buildfile)
                if target in build:
                    build = build[target]
                else:
                    print("ERROR: No target '" + target + "' in build.json")
                    sys.exit(2)
        except FileNotFoundError:
            print("ERROR: No build.json in", fluree_parts, "dir.")
            print("       Use --dir option to specify alternative build dir")
            return
        maxstage = 0
        # Outer loop for finding out where and how far to run the inner loop.
        # pylint: disable=too-many-nested-blocks
        testcount = 0
        for subdir in build:
            if output or notest:
                # If output or notest, we dont run any tests, we just fill the expanded list
                #  with expanded transactions.
                main = fluree_parts + "/" + subdir + "/main.json"
                noexpand = fluree_parts + "/" + subdir + ".json"
                if os.path.isfile(noexpand):
                    with open(noexpand) as nefile:
                        nelist = json.load(nefile)
                    for transaction in nelist:
                        out_transaction = list()
                        for operation in transaction:
                            if (verboseerrors and "_id" in operation and "id" in operation
                                    and operation["_id"].startswith("_rule")
                                    and "errorMessage" not in operation):
                                print("Adding verbose error for", operation["id"])
                                operation["errorMessage"] = "Verbose Errors: " + operation["id"]
                            out_transaction.append(operation)
                        expanded.append(out_transaction)
                else:
                    with open(main) as mainfile:
                        mainlist = json.load(mainfile)
                    for entry in mainlist:
                        expanded.append(expand_transaction(entry,
                                                           subdir,
                                                           fluree_parts,
                                                           verboseerrors))
            else:
                # Otherwise, if notest is false and the stage has a test.json,
                #  we run our inner loop for testing
                testfile = fluree_parts + "/" + subdir + "/test.json"
                if os.path.isfile(testfile) and not notest:
                    testcount += 1
                    # Make up a database name for our test, using network and stage name.
                    database = network + "/" + subdir
                    database = "-".join(database.lower().split("_"))
                    expanded2 = list()
                    expanded2.append(maxblock)
                    print("- Database:", database)
                    print(" - collecting transactions from build subdirs")
                    # Run the test with transactions from all stages up to this one.
                    print("Going through first", maxstage, "stages")
                    for subdir2 in build[:maxstage+1]:
                        print("  -", subdir2)
                        main = fluree_parts + "/" + subdir2 + "/main.json"
                        noexpand = fluree_parts + "/" + subdir2 + ".json"
                        if os.path.isfile(noexpand):
                            with open(noexpand) as nefile:
                                nelist = json.load(nefile)
                            for transaction in nelist:
                                transaction_out = list()
                                for operation in transaction:
                                    if (verboseerrors and "_id" in operation and "id" in operation
                                            and operation["_id"].startswith("_rule")
                                            and "errorMessage" not in operation):
                                        print("       + Adding verbose error for", operation["id"])
                                        operation["errorMessage"] = "Verbose Errors: " + \
                                                                    operation["id"]
                                    transaction_out.append(operation)
                                expanded2.append(transaction_out)
                        else:
                            with open(main) as mainfile:
                                mainlist = json.load(mainfile)
                            for entry in mainlist:
                                expanded2.append(expand_transaction(entry,
                                                                    subdir2,
                                                                    fluree_parts,
                                                                    verboseerrors))
                    # Run all test scenarios for this stage
                    await smartfunction_test(host,
                                             port,
                                             database,
                                             createkey,
                                             createid,
                                             build[maxstage],
                                             expanded2,
                                             fluree_parts)
            maxstage += 1
        if output:
            # Write the expanded transaction list for all stages combined to a single artifact.
            with open(output, "w") as opf:
                opf.write(json.dumps(expanded, indent=4))
        elif notest:
            # If no output but notest specified, fill the database with the expanded tranactions
            # list.
            database = network + "/" + target
            database = "-".join(database.lower().split("_"))
            await filldb(host, port, database, createkey, createid, expanded)
            print("Deployed", fluree_parts, "target", target, "to", database, "on", host)
        elif testcount == 0:
            print("WARNING: build target has no tests defined")
    except (RuntimeError, aioflureedb.FlureeException) as exp:
        # For a more friendly fail
        print(str(exp))
        sys.exit(1)
