import os
import json
try:
    import aioflureedb
except ModuleNotFoundError:
    pass
from fsst.fluree_do import do_transaction, do_query
from fsst.comments import strip_comments_obj, strip_comments_list

async def process_fluree_testfile(database,
                                  subdir,
                                  fluree_parts,
                                  fdb,
                                  transactionfile,
                                  succeed=True,
                                  keys=None,
                                  query=False):
    # pylint: disable=too-many-locals, too-many-arguments
    """Process a single query or transaction file from a test scenario directory

    Parameters
    ----------
    database: aioflureedb._FlureeDbClient
        FlureeQL DB Client using the priviledged "root" default signing key.
    subdir: string
        Test scenario subdir name
    fluree_parts: string
        Fluree build sources top dir directory path
    fdb: aioflureedb.FlureeClient
        Fluree Client for operations not linked to any particular database,
         such as database creation.
    transactionfile: str
        The file in the subdir we need to process.
    succeed: bool
        Boolean indicating if the transactions/queries in the file ar expected to succeed.
    keys: list,str,None
        List of key objects or a single key object containing the signing key and key id for running
        the transactions or queries with.
    query: bool
        Boolean indicating the file contains queries instead of transactions.

    Raises
    ------
    RuntimeError
        Problems with user.json content
    """
    basename = os.path.basename(transactionfile)
    print("   -", basename)
    # Read the file if it exists and fill a list of transactions/queries we should perform
    #  from its content.
    transactions = []
    if os.path.isfile(transactionfile):
        with open(transactionfile) as tfile:
            transactions = json.load(tfile)
    else:
        print("      - file not found, skipping:", basename)
    # The keys parameter is either a list of keys matching the list of transactions/queries,
    #  its a single key that should get used for all transaction/queries, or it is None.
    #  Normalize keys to the list variant.
    if not isinstance(keys, list):
        key = keys
        keys = []
        for transaction in transactions:
            keys.append(key)
    if len(keys) == len(transactions):
        # If keys has the proper length, everyting is irie and we process all queries/transactions
        for index, transaction in enumerate(transactions):
            key = keys[index]
            if key is None:
                # Strip transactions of any "COMMENT" fields.
                transaction = strip_comments_list(transaction)
                # If the key is None, this is probably the prepare or the cleanup file,
                #  run the transaction using the
                #  priviledged signing key
                await do_transaction(database, database, transaction, succeed)
            else:
                # Use the non-priv signing key for most operations
                async with fdb(key["private"], key["account-id"]) as database2:
                    if query:
                        # Strip all queries of any "COMMENT" fields.
                        transaction = strip_comments_obj(transaction)
                        # Run the query with the non-priv signing key
                        await do_query(database2, transaction, succeed)
                    else:
                        # Strip transactions of any "COMMENT" fields.
                        transaction = strip_comments_list(transaction)
                        # Run the transaction using the priviledged signing key, use the priv
                        #  signing key for transaction probing.
                        await do_transaction(database2, database, transaction, succeed)

        print("      - Ran", len(transactions), " database ", ("transactions", "queries")[query])
    else:
        print("      - ERROR: Wrong number of keys defined in user.json.")
        raise RuntimeError("Too many keys defined in user.json")


async def run_test_scenario(database, subdir, fluree_parts, fdb, scenario):
    """Run a single full test scenario

    Parameters
    ----------
    database: aioflureedb._FlureeDbClient
        FlureeQL DB Client using the priviledged "root" default signing key.
    subdir: string
        Test scenario subdir name
    fluree_parts: string
        Fluree build sources top dir directory path
    fdb: aioflureedb.FlureeClient
        Fluree Client for operations not linked to any particular database,
         such as database creation.
    scenario: str
        Name of the scenario sub-subdir
    """
    # pylint: disable=too-many-branches,too-many-arguments
    print("  - SCENARIO:", scenario)
    testdir = fluree_parts + "/" + subdir + "/" + scenario + "/"
    # Process the user.json file, this file contains the signing keys used in the scenario
    #  and designates what
    # signing key is used for what part of the test scenario.
    with open(testdir + "user.json") as userfile:
        users = json.load(userfile)
    yeskeys = []
    tyeskeys = []
    nokeys = []
    tnokeys = []
    if "yes" in users:
        if isinstance(users["yes"], list):
            for idx in users["yes"]:
                yeskeys.append(users["keys"][idx])
        else:
            yeskeys = users["keys"][users["yes"]]
    if "no" in users:
        if isinstance(users["no"], list):
            for idx in users["no"]:
                nokeys.append(users["keys"][idx])
        else:
            nokeys = users["keys"][users["no"]]
    if "tyes" in users:
        if isinstance(users["tyes"], list):
            for idx in users["tyes"]:
                tyeskeys.append(users["keys"][idx])
        else:
            tyeskeys = users["keys"][users["tyes"]]
    if "tno" in users:
        if isinstance(users["tno"], list):
            for idx in users["tno"]:
                tnokeys.append(users["keys"][idx])
        else:
            tnokeys = users["keys"][users["tno"]]
    # Process the rest of the files of the test scenario.
    #
    # Prepare transactions, these should at least create the users and give them the
    #  apropriate roles
    await process_fluree_testfile(database, subdir, fluree_parts, fdb, testdir + "prepare.json")
    # Run all yes queries, these should succeed with non empty results.
    await process_fluree_testfile(database, subdir, fluree_parts, fdb, testdir + "yes.json",
                                  keys=yeskeys, query=True)
    # Run all no queries, these should fail with empty results.
    await process_fluree_testfile(database, subdir, fluree_parts, fdb, testdir + "no.json",
                                  succeed=False, keys=nokeys, query=True)
    # Run all yes transactions, these should succeed without exceptions
    await process_fluree_testfile(database, subdir, fluree_parts, fdb,
                                  testdir + "tyes.json", keys=tyeskeys)
    # Run all no transactions, these should fail with exceptions from aioflureedb
    await process_fluree_testfile(database, subdir, fluree_parts, fdb,
                                  testdir + "tno.json", succeed=False, keys=tnokeys)
    # Run cleanup transactions
    await process_fluree_testfile(database, subdir, fluree_parts, fdb, testdir + "clean")


async def smartfunction_test(host, port, dbase, key, keyid, subdir, transactions, fluree_parts):
    """Create a test database, initialize database with transactions up to stage and run all
       tests for stage.

    Parameters
    ----------
    host: string
        The FlureeDB host
    port: int
        The TCP port of the FlureeDB host
    dbase: string
        The net/db string of the database on the FlureeDB host we want to submit the
        transactions to.
    key: string
        The ECDSA signing key for our transactions. This should be the host default key.
    keyid: string
        The key-id of the above signing key
    subdir: string
        The subdir name of the stage the tests are being ran for.
    transactions: list
        All transactions from the first till the current stage to run prior to test runs.
    fluree_parts:
        Fluree build sources top dir directory path


    Raises
    ------
    aioflureedb.FlureeException
        Exception from aioflureedb library in transaction
    """
    # pylint: disable=too-many-locals, too-many-arguments
    # Fluree host context, using priviledged (root role) default key.
    async with  aioflureedb.FlureeClient(masterkey=key, auth_address=keyid, host=host,
                                         port=port) as flureeclient:
        await flureeclient.health.ready()
        # Create the new database for our tests
        await flureeclient.new_db(db_id=dbase)
        fdb = await flureeclient[dbase]
        # Database context
        async with fdb(key, keyid) as database:
            await database.ready()
            # Run all the transactions in preparation to the tests
            print(" - processing schema transaction sub-set")
            for transaction in transactions:
                try:
                    await database.command.transaction(transaction)
                except aioflureedb.FlureeException as exp:
                    print("Exception while processing schema transaction")
                    print(json.dumps(transaction, indent=4, sort_keys=True))
                    print()
                    raise exp
            print(" - ok, completed", len(transactions), "transactions on", dbase)
            # Read the test scenario config file for this stage.
            with open(fluree_parts + "/" + subdir + "/test.json") as testscenariosfile:
                testscenarios = json.load(testscenariosfile)
            print(" - running test scenarios")
            # Run all test scenarios.
            for scenario in testscenarios:
                await run_test_scenario(database, subdir, fluree_parts, fdb, scenario)
            print(" -", len(testscenarios), "tests completed")
