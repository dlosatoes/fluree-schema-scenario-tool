#!/usr/bin/env python3
"""Simple script for compiling a fluree transaction init file, and for running
    basic tests with it"""
# pylint: disable=too-many-lines, unspecified-encoding, too-complex
import os
import os.path
import re
import copy
import subprocess
import webbrowser
import sys
import argparse
import json
import time
import asyncio
import itertools
import importlib.util
import requests
VERSION = "0.6.7"
CRYPTO_OK = True
DOCKER_OK = True
try:
    import aioflureedb
except ModuleNotFoundError:
    print("WARNING: - aioflureedb python lib not found.")
    CRYPTO_OK = False
if not CRYPTO_OK:
    print("         - testing commands disabled.")


def runs_in_docker():
    """Check if we are running inside of docker"""
    return os.path.isdir("/usr/src/fsst/fluree_parts")

try:
    import docker
except ModuleNotFoundError:
    if not runs_in_docker():
        print("WARNING: - docker python lib not found.")
        print("         - docker related commands disabled.")
    DOCKER_OK = False

# pylint: disable=consider-using-namedtuple-or-dataclass
AUTHMAP = {
    "auth00": ["TexyZ1iY2m8iHQoAGxvFd3e9ixWeUUjHdcG",
               "88a88244d7c7773f2378cd7adf37756c79171dea5f39588baf9b24b718317de9"],
    "auth01": ["TeyvAruG3UtLE1VCYRYxC2J69axvae7bstP",
               "629d1bc7a9ef7e37dbc96c1fed665f3d161053caffd41fe200215f55d0e5390c"],
    "auth02": ["TeyzwL1CwVu1zjnuxmfFa1VmgdnBgBV26mp",
               "abdec786a32ff02b0a184c84d47d00006b8489cfb759a519068b3e68ffcec21f"],
    "auth03": ["TezMZ3WGqsNnr1TbhvJfwSkZ25fCuzBiebY",
               "b26f86b1b978c999a2b5ae031ee46af7b061d6b4ba97c44b986eac9f9e0e2c51"],
    "auth04": ["TezYuxmu5RaW7gHrNCNEsfxpQmHhg3hDnJF",
               "1ab108dd3bca961186856c496e03bc470002fb497642e996d0ef01a177f184cf"],
    "auth05": ["Tf2kGuGjRsf64C1q3c8z9b5E7kEARdj6q86",
               "0257770de7ac12c0df2e5ba7d3454d67444705d29aec442b905eee8095b83fbc"],
    "auth06": ["Tf3Hdw7yzZefVXDwvX4VVEx2ybcoRDk3876",
               "e460310b2a5e98ecc8fc6b1bf0e1196e60c28977ea0a1c7ef7a537d6a8328e13"],
    "auth07": ["Tf4EKiRitki94Z3Kn5azaVgELp92ZeoBVXB",
               "cb034e7e300423a180c0bbf65799bc48d9fbdf9d9737b9cb649109d6d765f6fd"],
    "auth08": ["Tf5FLKYaRoPzKkkzMcstmQpqmDUnpGFQrxC",
               "5e3a6a2e91d8d2578233768932e9670f0903d3467df17f58100048d853b3bea8"],
    "auth09": ["Tf5LP9HuJVGmv8ipGfSwfz7Rs35AUf1jLtC",
               "670f8725350416ba39bde4de0404c1b79f310c8fd6e09ccbab9fd7562b751a99"],
    "auth10": ["Tf6u8HCXuzMcDp9T6FTVqvaXv5qULDJdXmw",
               "58c6f9a408b6db28d71b862b2a1ce7558f2520ba24360418ad346703aec70a94"],
    "auth11": ["Tf7iqsUXLitPaSNwrvYnftuPuYKmVwx5pV9",
               "04ad5ab2b4166ebcc78d886e509fbc4b9bd7ec749aed7629420fb5d6d1b18edf"],
    "auth12": ["Tf8JrKPiX3kpEZvU6FeCELpRotZW2e14SJk",
               "132e305bd87092b365162d9081f2fc5e4b3d8687a44d7f783b874cdf72b4f5c5"],
    "auth13": ["Tf8nJjKTQBtfXCoXFPa9DiXzBUJGF5pBxM4",
               "c9f97f1e5642eaa1062d6f5ed06a4bcc99299cab20962e3f183bd3b5afd27a86"],
    "auth14": ["TfALjQUSoupzGtkcqPzRbSevGBMYyu8EojD",
               "b8b2552084ccac35d450de138b188287496d4dec7a2926f01c3e6e11a587a1fa"],
    "auth15": ["TfATx8EUDmZ18cM6wRktKqpT1Lso41gUBwh",
               "de8ca443917ca63a92dec8271b8464b6e1b3f65bc9a0ed388bf2f32aab9003dc"],
    "auth16": ["TfCghFkQdz6hz5tmoxmxEAhAfrijbY5iukq",
               "e27b5a99f849a6ed44def9b9aa3c808412d2b3dafcc9aa2342ac813491049d9e"],
    "auth17": ["TfCt1WytKFAYRfpGDUpHPuxk1tzxAkNrFJp",
               "2ea9ce90c75b3c49438540f04b34b40fd87acebee35a6b93a49e012675fae396"],
    "auth18": ["TfENY4mnpDM26Bvb1Ff8SgRqGBMxgDQtRFP",
               "d889b413361cf532b49096d0db4ce98e1b4f8bf0a29684d8bb825a816ea21bdc"],
    "auth19": ["TfEoKNnfMeHoSLJq2qchHrrQoXeQqnEAdf4",
               "5552346ad862e1ccd81831336d710841b97477ed057c805d6be5997833210631"],
    "auth20": ["TfEVn9cKusd2K5smcRVhTE5XLjRe8XYJb4u",
               "e00b3e2029388ca6b0a469d4b2e759889f79beed33a6d0c54f22fd96ae3e995b"],
    "auth21": ["TfF3rpg2NfUa4BZb41pSTrHLeCMy13FatGd",
               "f568f2426d6cb02d4b61a3ce533f42904a4d5b59b1609203d783482a0143605b"],
    "auth22": ["TfFxqzzpf2MsvFTzxJFCwoPjmFsxS1FHe4y",
               "b624083aadb04222531b1c93da98e30281f75ce6e6b3bff2395950c6319947c1"],
    "auth23": ["TfJq331BRfL33w2yJgBV5uvrpsf7U34Uxi1",
               "5851fee3b9ea6873f1a9d10cadf2b562f3aa6853b8018e1ebeef322d297307d5"],
    "auth24": ["TfJVmmciLA9omhe2MUWiQY5ubXiQ5NT5g8a",
               "ffb82c8b047693cb4b61d34df6db3af3d7cce70fafa0c325cd14323dd961f63c"],
    "auth25": ["TfK2gUzJGF2Ag8Dc8cwJVKAzFqL2ADM4Y6M",
               "5dd01645ebd21e95e42c9038c407af890196c2fd309f114564d03709a15ce1aa"],
    "auth26": ["TfKCZCgyLQ28KMqiD4fgy9xz4jvfQWdgrQ6",
               "cc01464cdc0913d3643a6f9ea7d1393cd31c3ad011990fcbe83f1cdfc8b2362b"],
    "auth27": ["Tey7yFeGt5JfyGiGwdz8f4LmBCYfxqCk4VW",
               "875175ef14950c64d70b336ec15eb18210629a6083a87d5c329d977921f4df80"],
    "auth28": ["Tf6GnUYYz7ZtgQqBzs4rpqPqwpyycFAPKXy",
               "ef68a365b411126be8fbc3aefdf3c3f3ea65d0d297334dc0800612e4289f5225"],
    "auth29": ["Tez1NYTfDZRzjaAowoFTKFHQBw4Z6bDzSw8",
               "33b7299d3ebe5590aba6618f2369911faf98fb0853a85d6d4cdeae0a951fae9e"],
    "auth30": ["TfC9jrDs1PbXJtY5iJQCGSszs88xFBgZyKW",
               "09e65ff02f2e78379d753681ae37ca3964e72ec97765eb63e6b0b10533d34d26"],
    "auth31": ["Tf8JAdpa3MASMLdWtcTvayHKdWBngZcWW88",
               "7881f421654c8ca1ff085b57a5ce8cd230894a30c66432e19c68f6a96d22add9"]
}


class FlushFile:
    """Helper class for file like objects to always flush on write"""
    def __init__(self, file_descriptor):
        """Constructor
         Parameters
         ----------
         fd: string
             File handle to wrap
        """
        self.file_desc = file_descriptor

    def write(self, data):
        """Write and flush the data

        Parameters
        ----------
        data : str
           Data to write

        Returns
        -------
        int
            return code
        """
        ret = self.file_desc.write(data)
        self.file_desc.flush()
        return ret

    def writelines(self, lines):
        """Write lines and flush

        Parameters
        ----------
        lines: list
            Lines to write and flush

        Returns
        -------
        int
            Return code
        """
        ret = self.file_desc.writelines(lines)
        self.file_desc.flush()
        return ret

    def flush(self):
        """Just flush

        Returns
        -------
        int
            Return code
        """
        return self.file_desc.flush()

    def close(self):
        """Close the file

        Returns
        -------
        int
            Return code
        """
        return self.file_desc.close()

    def fileno(self):
        """Get file number from file handle

        Returns
        -------
        int
            File number
        """
        return self.file_desc.fileno()


sys.stdout = FlushFile(sys.stdout)  # Fix print() not always flushing when running in
#                                     linux docker on a windows host


def query_to_clojure(obj, params):
    """Convert a FlureeQL query to a clojure '(query (str ...) )' smart-function function body.

    Parameters
    ----------
    obj: dict
        Dict object containing a FlureeQL query
    params: list
        List of parameters to insert into clojure expression

    Returns
    -------
    str
        A clojure (str ) expression that builds the param substituted FlureeQL query as a string.

    Raises
    ------
    RuntimeError
        If PARAM count in JSON and params length don't match
    """
    # Serialize the query, sorted keys for deterministic substitution, no pretty printing
    data = json.dumps(obj, sort_keys=True)
    # Split the JSON into parts using 'PARAM' as seperator
    parts = data.split("PARAM")
    # Escape each JSON part by serializing as a JSON list and removing the qruare brackets
    escaped_parts = [json.dumps([part])[1:-1] for part in parts]
    # The amount of parts should be one more than the amount ot parameters
    if len(parts) != len(params) + 1:
        raise RuntimeError("Param count mismatch: " +
                           str(len(params)) +
                           " given " +
                           str(len(parts) - 1) +
                           " needed ; " +
                           data)
    # Interleave the escaped JSON parts and the parameters and put them in a (str ) clojure
    #  expression
    rval = " ".join(list(itertools.chain(*zip(["(query (str "] + params, escaped_parts))) + [") )"])
    return rval


def query_to_clojure_previous(obj, params):
    """Convert a FlureeQL query to a clojure '(query (str ...) )' smart-function function body.

    Parameters
    ----------
    obj: dict
        Dict object containing a FlureeQL query
    params: list
        List of parameters to insert into clojure expression

    Returns
    -------
    str
        A clojure (str ) expression that builds the param substituted FlureeQL query as a string.

    Raises
    ------
    RuntimeError
        If PARAM count in JSON and params length don't match
    """
    # Serialize the query, sorted keys for deterministic substitution, no pretty printing
    obj["block"] = 1234567890987  # magic number
    data = json.dumps(obj, sort_keys=True)
    # Split the JSON into parts using 'PARAM' as seperator
    parts = data.split("PARAM")
    # Escape each JSON part by serializing as a JSON list and removing the qruare brackets
    escaped_parts = [json.dumps([part])[1:-1] for part in parts]
    # The amount of parts should be one more than the amount ot parameters
    if len(parts) != len(params) + 1:
        raise RuntimeError("Param count mismatch: " +
                           str(len(params)) +
                           " given " +
                           str(len(parts) - 1) +
                           " needed ; " +
                           data)
    # Interleave the escaped JSON parts and the parameters and put them in a (str ) clojure
    #  expression
    rval = " ".join(list(itertools.chain(*zip(["(query (str "] + params, escaped_parts))) + [") )"])
    # Now do the same with our magic number
    parts = rval.split(str(obj["block"]))
    if len(parts) != 2:
        raise RuntimeError("Problem with block insertion query_to_clojure_previous")
    return parts[0] + '" (query lastBlock) "' + parts[1]


def expand_operation(operation, subdir, fluree_parts, verboseerrors):
    """Expand any "code_expand" or "code+from_query" in a single operation within a transaction

    Parameters
    ----------
    operation: dict
        FlureeQL operation object taken from within a transaction
    subdir: str
        Component directory name
    fluree_parts: str
        Fluree build sources top dir directory path
    verboseerrors: boolean
        Add extra errpr message to rules that don't define them
    Returns
    -------
    str
        Potentially expanded version of the supplied operation
    """
    # If the operation has a "params" field, use it, otherwise use empty list.
    params = []
    if (verboseerrors and "_id" in operation and "id" in operation
            and operation["_id"].startswith("_rule")
            and "errorMessage" not in operation):
        print("Adding verbose error for", operation["id"])
        operation["errorMessage"] = "Verbose Errors: " + operation["id"]
    if "params" in operation:
        params = operation["params"]
    if "code_expand" in operation:
        # Read the file designated in the code_expand field
        path = os.path.join(fluree_parts, subdir, operation["code_expand"])
        with open(path) as datafile:
            data = datafile.read()
            data = re.sub(' +', ' ', data.replace("\n", " "))
        if operation["code_expand"].split(".")[-1].lower() == "clj":
            # A clojure file contains the actual "code" content
            operation["code"] = data.rstrip()
        else:
            # A JSON file contains a JSON FlureeQL query that is converted to clojure code.
            obj = json.loads(data)
            operation["code"] = query_to_clojure(obj, params)
        # Remove the code_expand key/value
        del operation["code_expand"]
    operation2 = None
    if "code_from_query" in operation:
        if "block" not in operation["code_from_query"] and "name" in operation and subdir != ".":
            operation2 = copy.deepcopy(operation)
            operation2["name"] = operation["name"] + "_previous_block"
            if ("_id" in operation2 and isinstance(operation2["_id"], str) and
                    "$" in operation2["_id"]):
                operation2["_id"] = operation2["_id"] + "_previous_block"
            operation2["code"] = query_to_clojure_previous(operation2["code_from_query"], params)
            del operation2["code_from_query"]
        # Inlined FlureeQL JSON gets converted to clojure code.
        operation["code"] = query_to_clojure(operation["code_from_query"], params)
        # Remove the code_from_query key/value
        del operation["code_from_query"]
    return operation, operation2


def expand_transaction(transaction, subdir, fluree_parts, verboseerrors):
    """Expand any "code_expand" or "code+from_query" in a transaction

    Parameters
    ----------
    transaction: list
        FlureeQL transaction list
    subdir: str
        Component directory name
    fluree_parts: str
        Fluree build sources top dir directory path
    verboseerrors: boolean
        Add extra error messages to rules that don't define them.

    Returns
    -------
    str
        Potentially expanded version of the supplied transaction
    """
    rval = []
    for operation in transaction:
        op1, op2 = expand_operation(operation, subdir, fluree_parts, verboseerrors)
        rval.append(op1)
        if isinstance(op2, dict):
            rval.append(op2)
    return rval


async def filldb(host, port, dbase, key, transactions):
    """Run a collection if thransactions against the database

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
    transactions: list
        A list with Fluree transactions to execute.

    Raises
    ------
    aioflureedb.FlureeException
        If schema transaction is invalid

    """
    # pylint: disable=too-many-arguments
    async with aioflureedb.FlureeClient(masterkey=key,
                                        host=host,
                                        port=port) as flureeclient:
        await flureeclient.health.ready()
        await flureeclient.new_ledger(ledger_id=dbase)
        fdb = await flureeclient[dbase]
        async with fdb(key) as database:
            await database.ready()
            for transaction in transactions:
                try:
                    await database.command.transaction(transaction)
                except aioflureedb.FlureeException as exp:
                    print("Exception while processing schema transaction")
                    print(json.dumps(transaction, indent=4, sort_keys=True))
                    print()
                    raise exp
    return key


def strip_comments_obj(operation):
    """ Strip all "COMMENT" key key/value pairs from a dict.

    Parameters
    ----------
    operation: dict
        A FlureeQL operation or query

    Returns
    -------
    dict
        A copy of the supplied dict without any COMMENT key key/value data.
    """
    rval = {}
    for key in operation.keys():
        if key != "COMMENT":
            rval[key] = operation[key]
    return rval


def strip_comments_list(transaction):
    """ Strip all "COMMENT" key key/balue pairs from a list of dicts

    Parameters
    ----------
    transaction: list
        A FlureeQL transaction.

    Returns
    -------
    str
        A copy of the supplied transaction without any COMMENT key/value data in any of the
        operations.
    """
    rval = []
    for operation in transaction:
        rval.append(strip_comments_obj(operation))
    return rval


async def do_transaction(database, rdatabase, transaction, succeed):
    """Do a single FlureeDB transaction.
    Parameters
    ----------
    database: aioflureedb._FlureeDbClient
        Database client using a regular unpriv signing key
    rdatabase: aioflureedb._FlureeDbClient
        Database client using the default "root" signing key.
    transaction: list
        Transaction to attempt
    succeed: bool
        Boolean indicating if the caller "expects" the transaction to succeed or fail

    Raises
    ------
    aioflureedb.FlureeException
        If an unexpected exception happens in a transaction.
    RuntimeError
        If a transaction or query fails where it wasn't expected to or succeeds when it was
         expected to fail.
    """
    # pylint: disable=too-many-branches, too-many-statements, too-many-try-statements, while-used
    try:
        try:
            # Transact without waiting for the result, we'll loop for that later
            tid = await database.command.transaction(transaction, do_await=False)
        except aioflureedb.FlureeException as exp:
            print("Exception while processing transaction for NO transaction\n",
                  json.dumps(transaction, indent=4, sort_keys=True))
            raise exp
        cont = True
        count = 0
        # Loop untill we know if the transaction succeeded.
        while cont:
            count += 1
            try:
                # Query if the transaction result is known using the "root" DB connection
                status = await rdatabase.flureeql.query(select=["*"], ffrom=["_tx/id", tid])
            except aioflureedb.FlureeException as exp:
                print("Exception while querying for transaction state with FlureeDB default key\n",
                      json.dumps(transaction, indent=4, sort_keys=True),
                      "\n",
                      tid)
                raise exp
            try:
                # Do the same using the regular signing key
                status2 = await database.flureeql.query(select=["*"], ffrom=["_tx/id", tid])
            except aioflureedb.FlureeException as exp:
                print("Exception while querying for transaction state with RUN-AS key.\n",
                      json.dumps(transaction, indent=4, sort_keys=True),
                      "\n",
                      tid)
                raise exp
            if status:
                # The transaction has completed, check what happened
                cont = False
                if not status2:
                    # We didn't get a result with the regular signing key AFTER we did get one
                    # with the root signing key.
                    print("         - ERROR: User has insuficient rights for own transaction")
                    print(json.dumps(transaction, indent=4, sort_keys=True))
                    raise RuntimeError("Insuficient rights to read own transaction")
                if "error" in status[0]:
                    # First type of error
                    if succeed:
                        # Raise exception if we were expected to succeed.
                        print("         - ERROR: Unexpected error in YES transaction\n",
                              json.dumps(transaction, indent=4, sort_keys=True),
                              "\n",
                              status)
                        raise RuntimeError("Unexpected error in YES transaction")
                    # This was an expected error
                    print("         - NOTICE: Expected error in NO transaction\n",
                          "                 :", status[0]["error"])
                elif "_tx/error" in status[0]:
                    # Second type of error
                    if succeed:
                        # Raise exception if we were expected to succeed.
                        print("         - ERROR: Unexpected error in YES transaction\n",
                              json.dumps(transaction, indent=4, sort_keys=True),
                              "\n",
                              status)
                        raise RuntimeError("Unexpected error in YES transaction")
                    # This was an expected error
                    print("         - NOTICE: Expected error in NO transaction\n",
                          "                 :", status[0]["_tx/error"])
                elif not succeed:
                    # Raise an exception if the transaction was suposed to fail.
                    print("       - ERROR  : No error from no transaction\n",
                          json.dumps(transaction, indent=4, sort_keys=True),
                          "\n",
                          status)
                    raise RuntimeError("No error returned from NO transaction")
            else:
                # Log to console every 10 attempts of trying to check if transaction is done.
                if not count % 10:
                    print("     - waiting for transaction to finish")
                # Sleep for 100 msec before checking again
                await asyncio.sleep(0.1)
    except aioflureedb.FlureeException as exp:
        # We either succeeded or failed unexpectedly
        if succeed:
            # Log failing transaction on exception.
            print("Exception while processing transaction\n",
                  json.dumps(transaction, indent=4, sort_keys=True))
            raise exp
        print("        - Expected exception")


async def do_query(database, query, succeed):
    """Perform a Fluree query on the database.


    Parameters
    ----------
    database: aioflureedb._FlureeDbClient
        Database client using a regular unpriv signing ke
    query: dict
        FlureeQL query to attempt
    succeed: bool
        Boolean indicating if the caller "expects" the query to succeed or fail

    Raises
    ------
    RuntimeError
        Empty response to yes or non-empty reaponse to no query
    aioflureedb.FlureeException
        Exception was thrown by aioflureedb lib while performing query
    """
    # Exceptions in queries are never OK, query should return empty results on failure.
    try:
        response0 = await database.flureeql.query.raw(query)
    except aioflureedb.FlureeException as exp:
        print("Exception while processing query")
        print(json.dumps(query, indent=4, sort_keys=True))
        print()
        raise exp
    # Strip all _id only values  from the response
    response = []
    for obj in response0:
        if "_id" in obj:
            del obj["_id"]
        if obj:
            response.append(obj)
    if response0 and not response:
        print("        - NOTE: Non-empty response treated as functionally empty (only _id fields)")
    # On success we expect a non-empty result
    if succeed and response:
        print("Empty response on YES query")
        print(json.dumps(query, indent=4, sort_keys=True))
        raise RuntimeError("Empty response to YES query.")
    # On failure we expect an empty result
    if not succeed and response:
        print("Non-empty response on NO query")
        print(json.dumps(query, indent=4, sort_keys=True))
        print(json.dumps(response, indent=4, sort_keys=True))
        raise RuntimeError("Non-empty response to NO query.")


async def process_fluree_testfile(database,
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
        for trans in transactions:
            keys.append(key)
    if len(keys) == len(transactions):
        # If keys has the proper length, everyting is irie and we process all queries/transactions
        for index, transaction in enumerate(transactions):
            key = keys[index]
            # pylint: disable=consider-using-assignment-expr
            if key is None:
                # Strip transactions of any "COMMENT" fields.
                trans = strip_comments_list(transaction)
                # If the key is None, this is probably the prepare or the cleanup file,
                #  run the transaction using the
                #  priviledged signing key
                await do_transaction(database, database, trans, succeed)
            else:
                # Use the non-priv signing key for most operations
                async with fdb(key["private"]) as database2:
                    if query:
                        # Strip all queries of any "COMMENT" fields.
                        trans = strip_comments_obj(transaction)
                        # Run the query with the non-priv signing key
                        await do_query(database2, trans, succeed)
                    else:
                        # Strip transactions of any "COMMENT" fields.
                        trans = strip_comments_list(transaction)
                        # Run the transaction using the priviledged signing key, use the priv
                        #  signing key for transaction probing.
                        await do_transaction(database2, database, trans, succeed)

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
    testdir = os.path.join(fluree_parts, subdir, scenario)
    # Process the user.json file, this file contains the signing keys used in the scenario
    #  and designates what
    # signing key is used for what part of the test scenario.
    with open(os.path.join(testdir, "user.json")) as userfile:
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
    # Prepare transactions, these should at least create the users and give them the
    #  apropriate roles
    await process_fluree_testfile(database,
                                  fdb,
                                  os.path.join(testdir, "prepare.json"))
    # Run all yes queries, these should succeed with non empty results.
    await process_fluree_testfile(database,
                                  fdb,
                                  os.path.join(testdir, "yes.json"),
                                  keys=yeskeys,
                                  query=True)
    # Run all no queries, these should fail with empty results.
    await process_fluree_testfile(database,
                                  fdb,
                                  os.path.join(testdir, "no.json"),
                                  succeed=False,
                                  keys=nokeys,
                                  query=True)
    # Run all yes transactions, these should succeed without exceptions
    await process_fluree_testfile(database,
                                  fdb,
                                  os.path.join(testdir, "tyes.json"),
                                  keys=tyeskeys)
    # Run all no transactions, these should fail with exceptions from aioflureedb
    await process_fluree_testfile(database,
                                  fdb,
                                  os.path.join(testdir, "tno.json"),
                                  succeed=False,
                                  keys=tnokeys)
    # Run cleanup transactions
    await process_fluree_testfile(database,
                                  fdb,
                                  os.path.join(testdir, "cleanup.json"))


async def domainapi_test(host, port, dbase, key, tests, transactions, api_dir, api_modules):
    # pylint: disable=too-many-statements, too-many-branches
    """Create a test database, initialize database with transactions up to stage and run all
       domain-API tests for stage.

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
    tests: list
        A list with domain API test descriptions
    transactions: list
        All transactions from the first till the current stage to run prior to test runs.
    api_modules: list
        List of dynamically loaded Domain-API modules

    """
    # pylint: disable=too-many-locals, too-many-arguments
    # Fluree host context, using priviledged (root role) default key.
    async with aioflureedb.FlureeClient(masterkey=key, host=host,
                                        port=port) as flureeclient:
        await flureeclient.health.ready()
        for test_index, current_test in enumerate(tests):
            print(" ###", current_test["test"], "test_index =", test_index, "###")
            print(" ###", current_test["doc"], "###")
            coverage_treshold = current_test["coverage"]
            coverage = 0
            dbase_name = dbase if test_index == 0 else dbase + "-" + str(test_index) # pylint: disable=compare-to-zero
            # Create the new database for our tests
            await flureeclient.new_ledger(ledger_id=dbase_name)
            fdb = await flureeclient[dbase_name]
            # Database context
            async with fdb(key) as database:
                await database.ready()
                full_public_api_root = aioflureedb.domain_api.FlureeDomainAPI(api_dir, database, bigint_patch=False, debug_print=True)
                full_testing_api_root = aioflureedb.domain_api.FlureeDomainAPI(os.path.join(api_dir, "fsst"),
                                                                               database, bigint_patch=False, debug_print=True)
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
                print(" - ok, completed", len(transactions), "transactions on", dbase_name)
                await database.command.transaction(
                    [
                        {
                            "_id": "_auth",
                            "doc": key,
                            "id": val[0]
                        }
                        for key, val in AUTHMAP.items()
                    ])
                print(" - ok, added hard-coded _auth collection")
                if current_test["auth_roles"]:
                    await database.command.transaction(
                        [
                            {
                                "_id": ["_auth/id", current_test["addr"]],
                                "roles": [
                                    ["_role/id", role]
                                    for role in current_test["auth_roles"]
                                ]
                            }
                        ])
                    print(" - ok, added auth roles for", current_test["addr"], ":", current_test["auth_roles"])
                if current_test["auth_roles_prepare"]:
                    await database.command.transaction(
                        [
                            {
                                "_id": ["_auth/id", current_test["addr_prepare"]],
                                "roles": [
                                    ["_role/id", role]
                                    for role in current_test["auth_roles_prepare"]
                                ]
                            }
                        ])
                    print(" - ok, added auth roles for", current_test["addr_prepare"], ":",
                          current_test["auth_roles_prepare"])
                await database.command.transaction(
                    [
                        {
                            "_id": "_user",
                            "username": current_test["user"],
                            "auth": [
                                ["_auth/id", current_test["addr"]]
                            ]
                        }
                    ])
                print(" - ok, added test user", current_test["user"], current_test["addr"])
                await database.command.transaction(
                    [
                        {
                            "_id": "_user",
                            "username": current_test["user_prepare"],
                            "auth": [
                                ["_auth/id", current_test["addr_prepare"]]
                            ]
                        }
                    ])
                print(" - ok, added test user", current_test["user_prepare"], current_test["addr_prepare"])
                if current_test["user_roles"]:
                    await database.command.transaction(
                        [
                            {
                                "_id": ["_user/username", current_test["user"]],
                                "roles": [
                                    ["_role/id", role]
                                    for role in current_test["user_roles"]
                                ]
                            }
                        ])
                    print(" - ok, added user roleds for", current_test["user"])
                if current_test["user_roles_prepare"]:
                    await database.command.transaction(
                        [
                            {
                                "_id": ["_user/username", current_test["user_prepare"]],
                                "roles": [
                                    ["_role/id", role]
                                    for role in current_test["user_roles_prepare"]
                                ]
                            }
                        ])
                    print(" - ok, added user roles for", current_test["user_prepare"],
                          current_test["user_roles_prepare"])
                if current_test["test"] in api_modules:
                    tester = api_modules[current_test["test"]].DomainApiTest(
                        {
                            "auth_ids": {key: value[0] for (key, value) in AUTHMAP.items()},
                            "current": {
                                "database_name": dbase,
                                "test": current_test,
                                "test_index": test_index
                            },
                            "privileged": {
                                "auth_keys": {key: value[1] for (key, value) in AUTHMAP.items()},
                                "fdb": fdb,
                                "flureeclient": flureeclient,
                                "api_dir": api_dir
                            }
                        })
                    role_api = {}
                    test_api = {}
                    role_api["root"] = full_public_api_root.get_api_by_role(current_test["role"])
                    test_api["root"] = full_testing_api_root.get_api_by_role("root")
                    async with fdb(current_test["key"]) as user_database:
                        async with fdb(current_test["key_prepare"]) as user_database_prepare:
                            full_public_api = aioflureedb.domain_api.FlureeDomainAPI(api_dir, user_database, bigint_patch=False, debug_print=True)
                            full_public_api_prepare = aioflureedb.domain_api.FlureeDomainAPI(api_dir, user_database_prepare, bigint_patch=False, debug_print=True)
                            full_testing_api = aioflureedb.domain_api.FlureeDomainAPI(os.path.join(api_dir,
                                                                                                   "fsst"),
                                                                                      user_database,
                                                                                      bigint_patch=False,
                                                                                      debug_print=True)
                            full_testing_api_prepare = aioflureedb.domain_api.FlureeDomainAPI(os.path.join(api_dir,
                                                                                                           "fsst"),
                                                                                              user_database_prepare,
                                                                                              bigint_patch=False,
                                                                                              debug_print=True)
                            role_api["user"] = full_public_api.get_api_by_role(current_test["role"])
                            role_api["role"] = full_public_api_prepare.get_api_by_role(current_test["role"])
                            test_api["user"] = full_testing_api.get_api_by_role("test")
                            test_api["role"] = full_testing_api_prepare.get_api_by_role("test")
                            if getattr(tester, 'prepare', None) is not None:
                                print(" + Running prepare")
                                try:
                                    is_ok = await tester.prepare(role_api, test_api)
                                except Exception as ex:
                                    print("     ERROR : Exception in prepare of test no",
                                          test_index)
                                    raise ex
                                if isinstance(is_ok, bool):
                                    if not is_ok:
                                        raise RuntimeError("The prepare failed for test at index "
                                                           + str(test_index))
                                elif not is_ok[0]:
                                    raise RuntimeError("The prepare_user failed for test at index " +
                                                       str(test_index) + " : " + str(is_ok[1]))
                            for subtest in current_test["sub_tests"]:
                                subtest_name = subtest[0]
                                should_succeed = subtest[1]
                                warn_only = subtest[2]
                                methods = []
                                go_on = True
                                idx = 0
                                while go_on: # pylint: disable=while-used
                                    if getattr(tester, 'run_test_' + subtest_name + '_idx',
                                               None) is None:
                                        go_on = False
                                    else:
                                        methods.append('run_test_' + subtest_name + "_idx")
                                    # pylint: disable=compare-to-zero
                                    if (not go_on and idx == 0 and getattr(tester, 'run_test_' +
                                                                           subtest_name, None) is not
                                            None):
                                        methods.append('run_test_' + subtest_name)
                                        go_on = True
                                    idx += 1
                                methods.sort()
                                for method in methods:
                                    print(" + Running", method, "as", current_test["addr"])
                                    method_to_call = getattr(tester, method)
                                    # pylint: disable=broad-except
                                    try:
                                        is_ok = await method_to_call(role_api, test_api)
                                    except Exception as ex:
                                        print("    NOTICE: Exception cought in", method, ":", ex)
                                        is_ok = False
                                    # pylint: enable=broad-except
                                    if is_ok is None:
                                        print("     res=", is_ok, "Doesn't count to coverage.")
                                    elif isinstance(is_ok, bool):
                                        if is_ok == should_succeed:
                                            print("     res=", is_ok, "EXPECTED")
                                            coverage += 1
                                        elif warn_only:
                                            print("    WARNING: res=", is_ok, "NOT EXPECTED")
                                        else:
                                            print("    ERROR: res=", is_ok, "NOT EXPECTED")
                                            raise RuntimeError(
                                                "Unexpected result from method test for " +
                                                method + " at sub-test " + str(test_index))
                                    elif is_ok[0] == should_succeed:
                                        print("     res=", is_ok[0], "EXPECTED", is_ok[1])
                                        coverage += 1
                                    elif warn_only:
                                        print("    WARNING: res=", is_ok, "NOT EXPECTED")
                                    else:
                                        print("    ERROR: res=", is_ok, "NOT EXPECTED")
                                        raise RuntimeError("Unexpected result from method test for"
                                                           + " " + method + " at sub-test " +
                                                           str(test_index))
                            if current_test["run_scenarios"]:
                                index = 1
                                scenario = "scenario" + str(index)
                                scenario_method = getattr(tester, scenario, None)
                                while scenario_method is not None: # pylint: disable=while-used
                                    # pylint: disable=broad-except
                                    try:
                                        is_ok = await scenario_method(role_api, test_api)
                                    except Exception as ex:
                                        print("    NOTICE: Exception cought in", scenario, ":", ex)
                                        is_ok = False
                                    if is_ok is None:
                                        print("     res=", is_ok, "ignore")
                                    elif isinstance(is_ok, bool):
                                        if is_ok:
                                            print("     res=", is_ok)
                                        else:
                                            print("    ERROR: res=", is_ok, "NOT EXPECTED")
                                            raise RuntimeError(
                                                "Unexpected result from scenario for " +
                                                scenario + " at sub-test " + str(test_index))
                                    elif is_ok[0]:
                                        print("     res=", is_ok[0], is_ok[1])
                                    else:
                                        print("    ERROR: res=", is_ok[0], "NOT EXPECTED", is_ok[1])
                                        raise RuntimeError(
                                                "Unexpected result from scenario for " +
                                                scenario + " at sub-test " + str(test_index))
                                    index += 1
                                    scenario = "scenario" + str(index)
                                    scenario_method = getattr(tester, scenario, None)
                    if coverage_treshold > coverage:
                        raise RuntimeError("Coverage insufficient for test no " +
                                           str(test_index) + " : " + str(coverage_treshold) +
                                           " > " + str(coverage))
                else:
                    raise RuntimeError("No domain-API python testing module loaded for " +
                                       current_test["test"])


async def smartfunction_test(host, port, dbase, key, subdir, transactions, fluree_parts):
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
    async with aioflureedb.FlureeClient(masterkey=key, host=host,
                                        port=port) as flureeclient:
        print("Client created")
        await flureeclient.health.ready()
        print("Server ready, creating database", dbase)
        # Create the new database for our tests
        await flureeclient.new_ledger(ledger_id=dbase)
        print("Database created")
        fdb = await flureeclient[dbase]
        print("Database handle fetched")
        # Database context
        async with fdb(key) as database:
            print("Database handle context opened")
            await database.ready()
            print("Database ready")
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
            with open(os.path.join(fluree_parts, subdir, "test.json")) as testscenariosfile:
                testscenarios = json.load(testscenariosfile)
            print(" - running test scenarios")
            # Run all test scenarios.
            for scenario in testscenarios:
                await run_test_scenario(database, subdir, fluree_parts, fdb, scenario)
            print(" -", len(testscenarios), "tests completed")


async def fluree_main(notest, network, host, port, output, createkey,
                      target, fluree_parts, verboseerrors, api="apimap", stages="ALL"):
    # pylint: disable=too-many-branches, too-many-statements, fixme
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
        "name": "lastBlock",
        "doc": "Get the number of the last known block on the ledger",
        "code_from_query": {
            "select": "?maxBlock",
            "where": [
                ["?s", "_block/number", "?bNum"],
                ["?maxBlock", "#(max ?bNum)"],
                ["?s", "_block/number", "?maxBlock"]
            ]
        }
    }, ".", fluree_parts, False)[0]]
    allstages = False
    teststages = set()
    if stages == "ALL":
        allstages = True
    else:
        teststages = set(stages.split(","))
    print("DEBUG:", allstages, list(teststages))
    try:
        expanded = []
        expanded.append(maxblock)
        # Build.json contains the different build targets and lists their components.
        # Fetch the specified target from this file.
        try:
            with open(os.path.join(fluree_parts, "build.json")) as buildfile:
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
                main = os.path.join(fluree_parts, subdir, "main.json")
                noexpand = os.path.join(fluree_parts, subdir + ".json")
                if os.path.isfile(noexpand):
                    with open(noexpand) as nefile:
                        nelist = json.load(nefile)
                    for transaction in nelist:
                        out_transaction = []
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
                testfile = os.path.join(fluree_parts, subdir, "test.json")
                if os.path.isfile(testfile) and not notest and (allstages or subdir in teststages):
                    testcount += 1
                    # Make up a database name for our test, using network and stage name.
                    database = network + "/" + subdir
                    database = "-".join(database.lower().split("_"))
                    expanded2 = []
                    expanded2.append(maxblock)
                    print("- Database:", database)
                    print(" - collecting transactions from build subdirs")
                    # Run the test with transactions from all stages up to this one.
                    print("Going through first", maxstage+1, "stages")
                    for subdir2 in build[:maxstage+1]:
                        print("  -", subdir2)
                        main = os.path.join(fluree_parts, subdir2, "main.json")
                        noexpand = os.path.join(fluree_parts, subdir2 + ".json")
                        if os.path.isfile(noexpand):
                            with open(noexpand) as nefile:
                                nelist = json.load(nefile)
                            for transaction in nelist:
                                transaction_out = []
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
                    if allstages or build[maxstage] in teststages:
                        print("Running smartfunction_test")
                        await smartfunction_test(host,
                                                 port,
                                                 database,
                                                 createkey,
                                                 build[maxstage],
                                                 expanded2,
                                                 fluree_parts)
                    else:
                        print("Skipping tests for", build[maxstage])
                # If notest is false and the stage has a domain.json,
                #  we run domain-API tests
                testfile = os.path.join(fluree_parts, subdir, "domain.json")
                if os.path.isfile(testfile) and not notest and (allstages or subdir in teststages):
                    expanded2 = []
                    expanded2.append(maxblock)
                    # Make up a database name for our test, using network and stage name.
                    database = network + "/api_" + subdir
                    database = "-".join(database.lower().split("_"))
                    print("- Database:", database)
                    print(" - collecting transactions from build subdirs")
                    # Run the test with transactions from all stages up to this one.
                    print("Going through first", maxstage+1, "stages")
                    for subdir2 in build[:maxstage+1]:
                        print("  -", subdir2)
                        main = os.path.join(fluree_parts, subdir2, "main.json")
                        noexpand = os.path.join(fluree_parts, subdir2 + ".json")
                        if os.path.isfile(noexpand):
                            with open(noexpand) as nefile:
                                nelist = json.load(nefile)
                            for transaction in nelist:
                                transaction_out = []
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
                    with open(testfile) as testfil:
                        testsets = json.load(testfil)
                    if (os.path.isdir(api) and
                            os.path.isdir(os.path.join(api, "fsst")) and
                            os.path.isdir(os.path.join(api, "roles")) and
                            os.path.isdir(os.path.join(api, "fsst", "tests"))):
                        apimap_modules = {}
                        for modname in [fil[:-3] for fil in os.listdir(os.path.join(api,
                                                                                    "fsst",
                                                                                    "tests")) if
                                        fil[-3:] == ".py"]:
                            modpath = os.path.join(api, "fsst", "tests", modname + ".py")
                            spec = importlib.util.spec_from_file_location(modname, modpath)
                            apimap_modules[modname] = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(apimap_modules[modname])
                            if getattr(apimap_modules[modname], 'DomainApiTest', None) is None:
                                del apimap_modules[modname]
                            else:
                                print("NOTICE: Loaded Domain-API testing module", modname)
                        full_coverage = {}
                        for role in [fil[:-5] for fil in os.listdir(os.path.join(api, "roles")) if
                                     fil[-5:] == ".json"]:
                            full_coverage[role] = set()
                            with open(os.path.join(api, "roles", role + ".json")) as rolefile:
                                role_data = json.load(rolefile)
                            for key in role_data.keys():
                                for val in role_data[key]:
                                    full_coverage[role].add(val)
                        test_list = []
                        for test in testsets:
                            if "api_role" in test:
                                role = test["api_role"]
                                test_name = role
                                if "test" in test:
                                    test_name = test["test"]
                                if role in full_coverage:
                                    role_all = full_coverage[role]
                                    auth = "$auth00"
                                    auth_prepare = "$auth31"
                                    if "auth" in test:
                                        auth = test["auth"]
                                    if "auth_prepare" in test:
                                        auth_prepare = test["auth_prepare"]
                                    if auth[0] != "$":
                                        auth = "$auth00"
                                    if auth_prepare[0] != "$":
                                        auth_prepare = "$auth31"
                                    if auth[1:] in AUTHMAP:
                                        auth_info = AUTHMAP[auth[1:]]
                                        user = auth[1:]
                                    else:
                                        auth_info = AUTHMAP["auth00"]
                                        user = "auth00"
                                    if auth_prepare[1:] in AUTHMAP:
                                        auth_info_prepare = AUTHMAP[auth_prepare[1:]]
                                        user_prepare = auth_prepare[1:]
                                    else:
                                        auth_info_prepare = AUTHMAP["auth31"]
                                        user_prepare = "auth31"
                                    if "user" in test:
                                        user = test["user"]
                                    if "user_prepare" in test:
                                        user_prepare = test["user_prepare"]
                                    auth_roles = set()
                                    auth_roles_prepare = set()
                                    if "auth_roles" in test:
                                        auth_roles = set(test["auth_roles"])
                                    if "auth_roles_prepare" in test:
                                        auth_roles_prepare = set(test["auth_roles_prepare"])
                                    else:
                                        auth_roles_prepare = auth_roles
                                    user_roles = set()
                                    user_roles_prepare = set()
                                    if "user_roles" in test:
                                        user_roles = set(test["user_roles"])
                                    if "user_roles_prepare" in test:
                                        user_roles_prepare = set(test["user_roles_prepare"])
                                    else:
                                        user_roles_prepare = user_roles
                                    minimal_coverage = 100.0
                                    if "minimal_coverage" in test:
                                        minimal_coverage = float(test["minimal_coverage"])
                                    should_succeed = True
                                    if "should_succeed" in test:
                                        should_succeed = bool(test["should_succeed"])
                                    should_succeed_exceptions = set()
                                    if "should_succeed_exceptions" in test:
                                        should_succeed_exceptions = set(
                                            test["should_succeed_exceptions"])
                                    warn_only = False
                                    if "warn_only" in test:
                                        warn_only = bool(test["warn_only"])
                                    warn_only_exceptions = set()
                                    if "warn_only_exceptions" in test:
                                        warn_only_exceptions = set(test["warn_only_exceptions"])
                                    skip = set()
                                    if "skip" in test:
                                        skip = set(test["skip"])
                                    run_scenarios = True
                                    if "scenarios" in test and not test["scenarios"]:
                                        run_scenarios = False
                                    doc = "No doc for test"
                                    if "doc" in test:
                                        doc = test["doc"]
                                    role_used = set()
                                    for key in role_all:
                                        if key not in skip:
                                            role_used.add(key)
                                    should_succeed_map = {}
                                    warn_only_map = {}
                                    for key in role_used:
                                        if key in should_succeed_exceptions:
                                            should_succeed_map[key] = not should_succeed
                                        else:
                                            should_succeed_map[key] = should_succeed
                                        if key in warn_only_exceptions:
                                            warn_only_map[key] = not warn_only
                                        else:
                                            warn_only_map[key] = warn_only
                                    minimal_succeed_count = int((minimal_coverage + 0.01) *
                                                                len(should_succeed_map.keys()) /
                                                                100)
                                    test_obj = {}
                                    test_obj["role"] = role
                                    test_obj["test"] = test_name
                                    test_obj["addr"] = auth_info[0]
                                    test_obj["key"] = auth_info[1]
                                    test_obj["addr_prepare"] = auth_info_prepare[0]
                                    test_obj["key_prepare"] = auth_info_prepare[1]
                                    test_obj["auth_roles"] = list(auth_roles)
                                    test_obj["auth_roles_prepare"] = list(auth_roles_prepare)
                                    test_obj["user"] = user
                                    test_obj["user_prepare"] = user_prepare
                                    test_obj["user_roles"] = list(user_roles)
                                    test_obj["user_roles_prepare"] = list(user_roles_prepare)
                                    test_obj["sub_tests"] = []
                                    test_obj["run_scenarios"] = run_scenarios
                                    test_obj["doc"] = doc
                                    for key, val in should_succeed_map.items():
                                        test_obj["sub_tests"].append([key,
                                                                      val,
                                                                      warn_only_map[key]])
                                    test_obj["coverage"] = minimal_succeed_count
                                    test_list.append(test_obj)
                                else:
                                    print("WARNING: role", role, " defined in",
                                          testfile, "not defined in", os.path.join(api, "roles"))
                            else:
                                print("WARNING: test in", testfile,
                                      "without api_role, skipping tests")
                        await domainapi_test(host,
                                             port,
                                             database,
                                             createkey,
                                             test_list,
                                             expanded2,
                                             api,
                                             apimap_modules)
                    else:
                        print("WARNING: Skipping apimap tests because apimap dir is missing or",
                              "incomplete:", api)

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
            key = await filldb(host, port, database, createkey, expanded)
            print("Deployed", fluree_parts, "target", target, "to", database, "on", host,
                    "with key", key)
        elif testcount == 0: # pylint: disable=compare-to-zero
            print("WARNING: build target has no tests defined")
        return True
    except (RuntimeError, aioflureedb.FlureeException) as exp:
        print(exp)
        return False


def get_running_docker(client, tag):
    """Get the running docker"""
    name = "pibara/fsst:" + tag
    for container in client.containers.list():
        for ttag in container.image.attrs["RepoTags"]:
            if ttag == name:
                return container
    return None


def get_container_info(container):
    """Get host port and create key from docker"""
    hostport = None
    createkey = None
    if ("HostConfig" in container.attrs and "PortBindings" in container.attrs["HostConfig"]):
        for portoption in ["8090/tcp", "8090/tcp"]:
            if portoption in container.attrs["HostConfig"]["PortBindings"]:
                for binding in container.attrs["HostConfig"]["PortBindings"][portoption]:
                    if "HostPort" in binding:
                        hostport = binding["HostPort"]
    command_result = container.exec_run("cat default-private-key.txt")
    if command_result.exit_code == 0: # pylint: disable=compare-to-zero
        createkey = command_result.output.decode()
    return hostport, createkey


def get_from_docker(tag):
    """Retreive the host port and the createkey from a running fsst docker image"""
    client = docker.from_env()
    container = get_running_docker(client, tag)
    if not container:
        print("ERROR: Running docker with tag", tag, "not found")
        sys.exit(1)
    hostport, createkey = get_container_info(container)
    return hostport, createkey


def run_in_docker(tag, command, directory, daemonize, expose, api="apimap", debug=False):
    """Run a given command in a new docker container"""
    # pylint: disable=too-many-locals, too-many-statements, too-many-branches, too-many-arguments
    print("COMMAND:", command)
    match = None
    lookfor = "pibara/fsst:" + tag
    print("IMAGE:", lookfor)
    client = docker.from_env()
    for image in client.images.list():
        for repotag in image.attrs["RepoTags"]:
            if repotag == lookfor:
                match = image
    if match is None:
        print("NOTICE:", tag, "not found, trying to fetch from docker hubi, this may take a moment.")
        try:
            match = client.images.pull("pibara/fsst", tag=tag)
            print("  - Fetched")
        except requests.exceptions.HTTPError:
            print("ERROR: ", lookfor, "docker image not found")
            sys.exit(0)
    workdir = os.path.join(os.getcwd(), directory)
    if not os.path.isdir(workdir):
        print("ERROR:", workdir, "isn't a valid directory path")
        sys.exit(1)
    mounts = [docker.types.Mount("/usr/src/fsst/fluree_parts",
                                 workdir, read_only=True, type="bind")]
    apidir = os.path.join(os.getcwd(), api)
    if os.path.isdir(apidir):
        mounts.append(docker.types.Mount("/usr/src/fsst/apimap",
                                         apidir, read_only=True, type="bind"))
    ports = {}
    name = "fsst-guestcommand-" + tag
    if expose or daemonize:
        if tag == "stable":
            ports["8090/tcp"] = 8090
        else:
            ports["8090/tcp"] = 8090
    environment = {}
    if debug:
        environment["AIOFLUREEDB_DEBUG"] = "TRUE"
    try:
        container = client.containers.run(match, command, mounts=mounts, environment=environment,
                                          ports=ports, detach=True, auto_remove=True, name=name)
    except docker.errors.APIError as exp:
        print("ERROR: Problem starting docker container OR issue binding to 8090")
        print(exp)
        sys.exit(1)
    try:
        browser_triggered = False
        runcmd = container.logs(stream=True, follow=True)
        if daemonize:
            print("Starting fluree, waiting for fluree to initialize before daemonizing")
            print("Browser should start up, shortly")
        for line in runcmd:
            sline = line.decode().replace("\r", "").replace("\n", "")
            if not daemonize:
                print(sline, flush=True)
            if sline == "LINGER == True" and browser_triggered is False: # pylint: disable=compare-to-zero
                webbrowser.open("http://localhost:8090/")
                browser_triggered = True
                if daemonize:
                    runcmd.close()
                    break
    except KeyboardInterrupt:
        print("Stopping container")
        container.stop()
        print("Container stopped after keyboard interrupt")


async def get_createkey_and_port(createkey, keyfile, dockerfind,
                                 port, startfluree, verbosefluree):
    """Get the create-key and fluree port using the relevant commandline info"""
    # pylint: disable=too-many-arguments
    if startfluree:
        rval = None
        command = ["/bin/bash", "/usr/src/fsst/fluree_start.sh", "-Dfdb-api-port=8090"]
        if not verbosefluree:
            # pylint: disable=consider-using-with
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # pylint: disable=consider-using-with
            subprocess.Popen(command)
        times = 0
        while not rval: # pylint: disable=while-used
            try:
                with open("./default-private-key.txt") as kfile:
                    rval = kfile.read()
            except FileNotFoundError:
                print("# waiting for default-private-key.txt to appear")
            await asyncio.sleep(6)
            times += 1
            if times > 40:
                print("ERROR: Taking too long for default-private-key.txt to apear in docker")
                print("       container after starting FlureeDB")
                sys.exit(1)
        print("Started FlureeDB and got createkey from newly created keyfile")
        return rval, port
    if createkey:
        print("Using --createkey and --port values", )
        return createkey, port
    if keyfile:
        print("Using --keyfile and --port values")
        with open(keyfile) as kfil:
            createkey = kfil.read().replace("\r", "").replace("\n", "")
            return createkey, port
    if dockerfind:
        print("Fetching createkey and port from running image:", dockerfind)
        hostport, createkey = get_from_docker(dockerfind)
        return createkey, hostport
    print("ERROR: No way specfied to find default signing key for FlureeDB")
    print("       Use one of the following command line options:")
    print("")
    print("         --createkey")
    print("         --keyfile")
    print("         --dockerfind")
    sys.exit(1)


async def artifact_main(output, directory, target, verbose_errors):
    """Main function for the artifact sub command"""
    is_ok = await fluree_main(notest=False,
                              network=None,
                              host=None,
                              port=None,
                              output=output,
                              createkey=None,
                              target=target,
                              fluree_parts=directory,
                              verboseerrors=verbose_errors)
    if not is_ok:
        sys.exit(1)
    return


async def test_main(directory, target, verboseerrors, host, port,
                    network, createkey, api, stages):
    """Main function for the test subcommand"""
    # pylint: disable=too-many-arguments
    is_ok = await fluree_main(notest=False,
                              network=network,
                              host=host,
                              port=port,
                              output=None,
                              createkey=createkey,
                              target=target,
                              fluree_parts=directory,
                              verboseerrors=verboseerrors,
                              api=api,
                              stages=stages)
    if not is_ok:
        sys.exit(1)
    return


async def deploy_main(directory, target, verboseerrors, host, port, network, createkey):
    """Main function for the deploy subcommand"""
    # pylint: disable=too-many-arguments
    is_ok = await fluree_main(notest=True,
                              network=network,
                              host=host,
                              port=port,
                              output=None,
                              createkey=createkey,
                              target=target,
                              fluree_parts=directory,
                              verboseerrors=verboseerrors)
    if not is_ok:
        sys.exit(1)
    return


async def dockertest_main(directory, target, verboseerrors,
                          network, tag, verbosefluree, linger, api, stages, debug):
    """Main function for the dockertest subcommand"""
    # pylint: disable=too-many-arguments
    cmd = "fsst guesttest --target " + target + " --network " + network
    if verboseerrors:
        cmd += " --verboseerrors"
    if verbosefluree:
        cmd += " --verbosefluree"
    if linger:
        cmd += " --linger"
    cmd += " --stages " + stages
    return run_in_docker(tag, cmd, directory, False, linger, api=api, debug=debug)


async def dockerstart_main(tag):
    """Main function for the dockerstart subcommand"""
    imagename = "pibara/fsst:" + tag
    fluree_command = "/bin/bash /usr/src/fsst/fluree_start.sh  -Dfdb-api-port=8090"
    ports = {}
    if tag == "stable":
        ports["8090/tcp"] = 8090
    else:
        ports["8090/tcp"] = 8090
    client = docker.from_env()
    name = "fsst-dockerstart-" + tag
    try:
        client.containers.run(imagename, fluree_command, ports=ports,
                              detach=True, auto_remove=True, name=name)
        print("Started", imagename)
    except docker.errors.NotFound:
        print("ERROR:", imagename, "not found")
    return


async def dockerstop_main(tag):
    """Main function for the dockerstop subcommand"""
    lookfor = "pibara/fsst:" + tag
    client = docker.from_env()
    container = get_running_docker(client, tag)
    if container:
        container.stop()
        print("Stopping", lookfor)
    else:
        print("ERROR: no running instance of", lookfor, "found")


async def versioncheck_main(tag):
    """Main function for the versioncheck subcommand"""
    # pylint: disable=too-many-branches
    match = None
    lookfor = "pibara/fsst:" + tag
    client = docker.from_env()
    for image in client.images.list():
        for repotag in image.attrs["RepoTags"]:
            if repotag == lookfor:
                match = image
    if match is None:
        print("ERROR: ", lookfor, "docker image not found")
        sys.exit(0)
    cmd = "fsst version"
    name = "fsst-versioncheck-" + tag
    try:
        container = client.containers.run(match, cmd, detach=False, auto_remove=True, name=name)
    except docker.errors.ContainerError:
        print("ERROR: Container Error.")
        print("       This might be the result of a 0.1.x version of the docker container")
        print("       that didn't support --version yet")
        sys.exit(1)
    dockerfsstversion = None
    for line in container.decode().split("\n"):
        parts = line.split(":")
        if len(parts) == 2 and parts[0] == "FSST VERSION":
            dockerfsstversion = parts[1].replace(" ", "")
            dockerfsst = dockerfsstversion.split(".")
    if not dockerfsstversion:
        print("ERROR: No valid response to --version from fsst in docker.")
        print("       This might be the result of a 0.1.x version of the docker container")
        print("       that didn't support --version yet")
        sys.exit(1)
    localfsst = VERSION.split(".")
    if dockerfsst[0] == localfsst[0]:
        if dockerfsst[1] == localfsst[1]:
            if dockerfsst[2] == localfsst[2]:
                print("Perfect version match:", VERSION, "for image", lookfor)
            else:
                print("Near version match:", VERSION, "local vs", dockerfsstversion,
                      "in docker image", lookfor, ". Should be OK.")
        else:
            print("NOTICE: Possible version mismatch:", VERSION, "local vs", dockerfsstversion,
                  "in docker image", lookfor, "Use with care.")
    else:
        print("WARNING: Version mismatch:", VERSION, "local vs", parts[1], "in docker image",
              lookfor)
        sys.exit(1)
    return


async def dockerdeploy_main(directory, target, verboseerrors, dbase, tag, verbosefluree, daemonize, debug):
    """Main function for the dockerdeploy subcommand"""
    # pylint: disable=too-many-arguments
    cmd = "fsst guestdeploy " + dbase + " --target " + target + \
          " --linger"
    if verboseerrors:
        cmd += " --verboseerrors"
    if verbosefluree or not daemonize:
        cmd += " --verbosefluree"
    return run_in_docker(tag, cmd, directory, daemonize, True, debug=debug)


async def guesttest_main(target, verboseerrors, network, linger, createkey, stages):
    """Main function for the guesttest subcommand"""
    # pylint: disable=too-many-arguments
    prt = 8090
    is_ok = await fluree_main(notest=False,
                              network=network,
                              host="localhost",
                              port=prt,
                              output=None,
                              createkey=createkey,
                              target=target,
                              fluree_parts="fluree_parts",
                              verboseerrors=verboseerrors,
                              stages=stages)
    if linger:
        print("LINGER == True")
        count = 0
        while True: # pylint: disable=while-used
            await asyncio.sleep(30)
            count += 1
            print('LINGER', count, flush=True)
    if not is_ok:
        sys.exit(1)
    return


async def artifactdeploy_main(inputfile, dbase, host, port, createkey):
    # pylint: disable=too-many-arguments
    """Main function for the artifactdeploy subcommand"""
    try:
        with open(inputfile) as artifactfile:
            artifactdata = artifactfile.read()
        artifact = json.loads(artifactdata)
    except FileNotFoundError:
        print("ERROR: couldn't open file:", inputfile)
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        print("ERROR: Not a JSON file:", inputfile)
        sys.exit(1)
    if not isinstance(artifact, list):
        print("ERROR: Artifact file should contain a JSON array:", inputfile)
        sys.exit(1)
    for transaction in artifact:
        if not isinstance(transaction, list):
            print("ERROR: Artifact file should contain a JSON array of arrays:", inputfile)
            sys.exit(1)
        for operation in transaction:
            if not isinstance(operation, dict):
                print("ERROR: Artifact file should contain a JSON array of arrays of dicts:",
                      inputfile)
                sys.exit(1)
    async with aioflureedb.FlureeClient(masterkey=createkey,
                                        host=host,
                                        port=port) as flureeclient:
        await flureeclient.health.ready()
        # Create the new database for our tests
        try:
            await flureeclient.new_ledger(ledger_id=dbase)
        except aioflureedb.FlureeHttpError as exp:
            print("ERROR: Problem creating the database for deploy")
            print("      ", json.loads(exp.args[0])["message"])
            sys.exit(1)
        fdb = await flureeclient[dbase]
        # Database context
        async with fdb(createkey) as database:
            await database.ready()
            for transaction in artifact:
                try:
                    await database.command.transaction(transaction)
                except aioflureedb.FlureeException:
                    print("Exception while processing artifact transaction")
                    print(json.dumps(transaction, indent=4, sort_keys=True))
                    print()
                    sys.exit(1)
    print("Deployed", inputfile, "to", dbase, "on", host)
    return


async def dockerparams_main(tag):
    """Main function for the dockerparams subcommand"""
    client = docker.from_env()
    container = get_running_docker(client, tag)
    if container is None:
        print("ERROR, running container not found for tag =", tag)
        return
    echo = container.exec_run("cat default-private-key.txt")
    createkey = None
    port = None
    if echo.exit_code == 0: # pylint: disable=compare-to-zero
        createkey = echo.output.decode()
    if ("HostConfig" in container.attrs and
            "PortBindings" in container.attrs["HostConfig"] and
            "8090/tcp" in container.attrs["HostConfig"]["PortBindings"] and
            container.attrs["HostConfig"]["PortBindings"]["8090/tcp"]):
        for binding in container.attrs["HostConfig"]["PortBindings"]["8090/tcp"]:
            if "HostPort" in binding:
                port = int(binding["HostPort"])
    print("IMAGE:", tag)
    print("CREATEKEY:", createkey)
    print("PORT:", port)


async def guestdeploy_main(target, verboseerrors, dbase, createkey):
    """Main function for the guestdeploy subcommand"""
    prt = 8090
    is_ok = await fluree_main(notest=True,
                              network=None,
                              host=None,
                              port=None,
                              output="artifact.json",
                              createkey=None,
                              target=target,
                              fluree_parts="fluree_parts",
                              verboseerrors=verboseerrors)
    if is_ok:
        is_ok = await artifactdeploy_main("artifact.json", dbase, "localhost", prt, createkey)
    print("LINGER == True")
    count = 0
    while True: # pylint: disable=while-used
        await asyncio.sleep(30)
        count += 1
        print('LINGER', count, flush=True)
    if not is_ok:
        sys.exit(1)


def apiartifact_main(api, output_js, roles, output, force):
    # pylint: disable=too-many-branches, too-many-statements, too-many-locals
    """Main function of the apiartifact subcommand"""
    testdirs = [api]
    for subdir in ("roles", "query", "transaction"):
        testdirs.append(os.path.join(api, subdir))
    for path in testdirs:
        if not os.path.isdir(path):
            print("ERROR: Required dir doesn't exist or isn't a directory:", path)
            sys.exit(2)
    rolesdir = os.path.join(api, "roles")
    if roles == "ALL":
        my_roles = []
        for filename in os.listdir(rolesdir):
            filepath = os.path.join(rolesdir, filename)
            if os.path.isfile(filepath):
                name, ext = filename.split(".")
                if ext.lower() == "json":
                    my_roles.append(name)

    else:
        my_roles = roles.split(",")
    desired = {}
    desired["roles"] = set(my_roles)
    desired["queries"] = set()
    desired["multi"] = set()
    desired["transactions"] = set()
    found_roles = set()
    for filename in os.listdir(rolesdir):
        filepath = os.path.join(rolesdir, filename)
        if os.path.isfile(filepath):
            parts = filename.split(".")
            if len(parts) == 2:
                name, ext = filename.split(".")
                if ext.lower() == "json" and name in desired["roles"]:
                    found_roles.add(name)
                    with open(filepath) as infil:
                        obj = json.load(infil)
                        if "queries" in obj:
                            for query in obj["queries"]:
                                desired["queries"].add(query)
                        if "transactions" in obj:
                            for query in obj["transactions"]:
                                desired["transactions"].add(query)
                        if "multi" in obj:
                            for query in obj["multi"]:
                                desired["multi"].add(query)
    if bool(desired["roles"] - found_roles):
        print("ERROR: One or more designated roles not found in domain-API definition")
        for role in desired["roles"] - found_roles:
            print("  -", role)
        sys.exit(3)
    if os.path.exists(output):
        if not (os.path.isfile(output) and force):
            print(output, "file already exists:", output)
            sys.exit(2)
    obj = {}
    obj["roles"] = {}
    obj["query"] = {}
    obj["xform"] = {}
    obj["multi"] = {}
    obj["transaction"] = {}
    # pylint: disable=too-many-nested-blocks
    for subdir in ("roles", "query", "transaction", "multi"):
        fulldir = os.path.join(api, subdir)
        if os.path.isdir(fulldir):
            print(fulldir)
            for filename in os.listdir(fulldir):
                filepath = os.path.join(fulldir, filename)
                if os.path.isfile(filepath):
                    parts = filename.split(".")
                    if len(parts) == 2:
                        print(" *", filepath)
                        name, ext = filename.split(".")
                        if ext.lower() == "json":
                            # pylint: disable=too-many-boolean-expressions
                            if (subdir == "query" and
                                    name in desired["queries"] or
                                    subdir == "multi" and
                                    name in desired["multi"] or
                                    subdir == "transaction" and
                                    name in desired["transactions"] or
                                    subdir == "roles" and
                                    name in desired["roles"]):
                                with open(filepath) as infil:
                                    obj[subdir][name] = json.load(infil)
                                    if subdir == "query" and name not in obj["xform"]:
                                        obj["xform"][name] = "$"
                        elif (subdir in {"query", "multi"} and
                              ext.lower() == "xform" and
                              name in desired["queries"]):
                            with open(filepath) as infil:
                                obj["xform"][name] = infil.read()
                elif (os.path.isdir(filepath) and
                      subdir == "transaction" and
                      filename in desired["transactions"]):
                    subsubdir = os.path.join(fulldir, filename)
                    for subfilename in os.listdir(subsubdir):
                        subfilepath = os.path.join(subsubdir, subfilename)
                        if os.path.isfile(subfilepath):
                            name2, _ = subfilename.split(".")
                            if ext.lower() == "json":
                                with open(subfilepath) as infil2:
                                    if name2 == "default":
                                        obj["transaction"][filename] = json.load(infil2)
                                    else:
                                        obj["transaction"][filename + "/" + name2] = json.load(infil2)
    with open(output, "w") as outfil:
        if output_js:
            outfil.write("export let domain_api = ")
        json.dump(obj, outfil, indent=4, sort_keys=True)
        if output_js:
            outfil.write(";")
    print("Created", output)


async def argparse_main():
    # pylint: disable=too-many-statements,too-many-branches,too-many-locals
    """The main for the argparse subcommand"""
    netname = "test" + str(int(time.time()/10) % 100000)
    parsers = {}
    parsers["main"] = argparse.ArgumentParser()
    subparsers = parsers["main"].add_subparsers()
    # pylint: disable=line-too-long
    helps = {
        "artifact": "From a build target, create a single JSON artifact file with all transactions",
        "test": "Run tests for build target using a running FlureeDB",
        "dockertest": "Run tests for build target on a to be spawned docker containing FlureeDB",
        "deploy": "Deploy a build target to a running FlureeDB",
        "dockerdeploy": "Start a docker container, deploy build target, and keep container running",
        "guesttest": "DON'T USE, INTERNAL USE ONLY",
        "guestdeploy": "DON'T USE, INTERNAL USE ONLY",
        "dockerparams": "Fetch createkey and port from RUNNING fsst docker container",
        "artifactdeploy": "Deploy an artifact that was created with 'fsst artifact' earlier",
        "versioncheck": "Validate that the version of fsst invoked and the one inside of the docker image match",
        "version": "Get the version of the fsst tool",
        "dockerstart": "Start a flureeDB only instance of the fsst docker image, available on localhost:8090",
        "dockerstop": "Stop any running instance of the fsst docker image with the given tag",
        "apiartifact": "Create a single-file domain-API JSON artifact",
        "dir": "Directory containing build tree (default fluree_parts)",
        "api": "Directory containing domain-API mappings (default apimap)",
        "target": "FlureeDB, build target as defined in build.json ('default' if undefined)",
        "verboseerrors": "Add verbose errors to rules without an error defined.",
        "host": "FlureeDB host. (default localhost)",
        "port": "FlureeDB port. (default 8090)",
        "network": "FlureeDB network name. (generate if unspecified)",
        "createkey": "FlureeDB signing key for creation (alternative for --keyfile or --dockerfind)",
        "keyfile": "File containing FlureeDB signing key for creation",
        "dockerfind": "Extract FlureeDB signing key for creation from running docker",
        "linger": "Keep docker/FlureeDB running after tests have completed",
        "tag": "Tag to use for fsst docker image.",
        "verbosefluree": "Dont redirect flureedb stdout/stderr to /dev/null",
        "daemonize": "Run docker/FlureeDB docker as a daemon process",
        "output": "Output JSON file",
        "input": "Input JSON file",
        "db": "Name for the new database to deploy to.",
        "js": "Output a JavaScript module file instead of a JSON file",
        "roles": "Comma seperated list of roles to include in the domain-API artifact",
        "force": "Overwrite output file if it already exists",
        "stages": "Comma seperrated list of stages to run tests for. If none specified, then all tests will be run.",
        "debug": "Run aioflureedb in debug mode"
    }
    # pylint: enable=line-too-long
    defaults = {
        "dir": "fluree_parts",
        "api": "apimap",
        "target": "default",
        "verboseerrors": False,
        "js": False,
        "host": "localhost",
        "port": "8090",
        "network": netname,
        "createkey": None,
        "keyfile": None,
        "dockerfind": "stable",
        "linger": False,
        "tag": "stable",
        "verbosefluree": False,
        "daemonize": False,
        "roles": "ALL",
        "force": False,
        "stages": "ALL",
        "debug": False
    }
    argsmap = {
        "artifact": {"output", "dir", "target", "verboseerrors"},
        "test": {
            "dir",
            "api",
            "target",
            "verboseerrors",
            "host",
            "port",
            "network",
            "createkey",
            "keyfile",
            "dockerfind",
            "stages"
        },
        "deploy": {
            "dir",
            "target",
            "verboseerrors",
            "host",
            "port",
            "network",
            "createkey",
            "keyfile",
            "dockerfind"
        },
        "dockertest": {"dir",
                       "api",
                       "target",
                       "verboseerrors",
                       "network",
                       "linger",
                       "tag",
                       "verbosefluree",
                       "stages",
                       "debug"},
        "dockerdeploy": {"db", "dir", "target", "verboseerrors", "tag", "daemonize", "debug"},
        "dockerparams": {"tag"},
        "artifactdeploy": {"input:db", "host", "port", "createkey", "keyfile", "dockerfind"},
        "guesttest": {"target",
                      "verboseerrors",
                      "network",
                      "keyfile",
                      "linger",
                      "verbosefluree",
                      "api",
                      "stages"},
        "guestdeploy": {"db", "target", "verboseerrors", "keyfile", "linger", "verbosefluree"},
        "versioncheck": {"tag"},
        "dockerstart": {"tag"},
        "dockerstop": {"tag"},
        "version": {},
        "apiartifact": {"js", "api", "roles", "force", "output"}
    }
    if CRYPTO_OK:
        if DOCKER_OK:
            if runs_in_docker():
                subcommands = ["artifact",
                               "test",
                               "deploy",
                               "dockertest",
                               "dockerdeploy",
                               "guesttest",
                               "guestdeploy",
                               "version",
                               "apiartifact"]
            else:
                subcommands = ["artifact",
                               "test",
                               "deploy",
                               "dockertest",
                               "dockerdeploy",
                               "dockerparams",
                               "artifactdeploy",
                               "version",
                               "versioncheck",
                               "dockerstart",
                               "dockerstop",
                               "apiartifact"]
        elif runs_in_docker():
            subcommands = ["artifact",
                           "test",
                           "deploy",
                           "guesttest",
                           "guestdeploy",
                           "version",
                           "apiartifact"]
        else:
            subcommands = ["artifact",
                           "test",
                           "deploy",
                           "version",
                           "apiartifact"]
    else:
        subcommands = ["artifact"]
    for subcommand in subcommands:
        sc_help = helps[subcommand]
        sc_args = argsmap[subcommand]
        parsers[subcommand] = subparsers.add_parser(subcommand, help=sc_help)
        parsers[subcommand].add_argument('--subcommand', help=argparse.SUPPRESS, default=subcommand)
        todo = {
            "dir",
            "api",
            "target",
            "verboseerrors",
            "host",
            "port",
            "network",
            "createkey",
            "keyfile",
            "dockerfind",
            "linger",
            "tag",
            "verbosefluree",
            "output",
            "input",
            "db",
            "daemonize",
            "js",
            "roles",
            "force",
            "stages",
            "debug"
        }
        for sc_arg in sc_args:
            for subarg in sc_arg.split(":"):
                sa_help = helps[subarg]
                if subarg in defaults:
                    sa_default = defaults[subarg]
                    if sa_default is not None and not sa_default:
                        parsers[subcommand].add_argument('--' + subarg,
                                                         action='store_true',
                                                         help=sa_help)
                    else:
                        parsers[subcommand].add_argument("--" + subarg,
                                                         help=sa_help,
                                                         default=sa_default)
                else:
                    parsers[subcommand].add_argument(subarg, help=sa_help)
                todo.remove(subarg)
        for subarg in todo:
            parsers[subcommand].add_argument('--' + subarg, help=argparse.SUPPRESS, default=None)
    args = parsers["main"].parse_args()
    if not vars(args):
        print("Please supply commandline agruments. Use --help for info")
        sys.exit(1)
    if args.subcommand == "artifact":
        return await artifact_main(args.output, args.dir, args.target, args.verboseerrors)
    createkey = args.createkey
    port = args.port
    if args.subcommand in {"test", "deploy", "guesttest", "guestdeploy", "artifactdeploy"}:
        startfluree = bool(args.subcommand in {"guesttest", "guestdeploy"})
        createkey, port = await get_createkey_and_port(args.createkey,
                                                       args.keyfile,
                                                       args.dockerfind,
                                                       args.port,
                                                       startfluree,
                                                       args.verbosefluree)
    if args.subcommand == "test":
        await test_main(args.dir,
                        args.target,
                        args.verboseerrors,
                        args.host,
                        port,
                        args.network,
                        createkey,
                        args.api,
                        args.stages)
    elif args.subcommand == "deploy":
        await deploy_main(args.dir,
                          args.target,
                          args.verboseerrors,
                          args.host,
                          port, args.network,
                          createkey)
    elif args.subcommand == "dockertest":
        await dockertest_main(args.dir,
                              args.target,
                              args.verboseerrors,
                              args.network,
                              args.tag,
                              args.verbosefluree,
                              args.linger,
                              args.api,
                              args.stages,
                              args.debug)
    elif args.subcommand == "dockerdeploy":
        await dockerdeploy_main(args.dir,
                                args.target,
                                args.verboseerrors,
                                args.db,
                                args.tag,
                                args.verbosefluree,
                                args.daemonize,
                                args.debug)
    elif args.subcommand == "guesttest":
        await guesttest_main(args.target,
                             args.verboseerrors,
                             args.network,
                             args.linger,
                             createkey,
                             args.stages)
    elif args.subcommand == "guestdeploy":
        await guestdeploy_main(args.target, args.verboseerrors, args.db, createkey)
    elif args.subcommand == "artifactdeploy":
        await artifactdeploy_main(args.input, args.db, args.host, port, createkey)
    elif args.subcommand == "dockerparams":
        await dockerparams_main(args.tag)
    elif args.subcommand == "version":
        print("FSST VERSION:", VERSION)
    elif args.subcommand == "versioncheck":
        await versioncheck_main(args.tag)
    elif args.subcommand == "dockerstart":
        await dockerstart_main(args.tag)
    elif args.subcommand == "dockerstop":
        await dockerstop_main(args.tag)
    elif args.subcommand == "apiartifact":
        apiartifact_main(args.api, args.js, args.roles, args.output, args.force)
    else:
        print("ERROR: impossible subcommand:", args.subcommand)


def _main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(argparse_main())

if __name__ == '__main__':
    _main()
