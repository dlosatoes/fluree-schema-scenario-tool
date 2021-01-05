import asyncio
import json
import aioflureedb

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
    # pylint: disable=too-many-branches, too-many-statements
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
                    if succeed:
                        # If we were expected to succeed, this is a hard error
                        print("         - ERROR: User has insuficient rights for own transaction")
                        print(json.dumps(transaction, indent=4, sort_keys=True))
                        raise RuntimeError("Insuficient rights to read own transaction")
                    # If we were expected to fail, this still is something we need to warn about.
                    # Its probably good to allow any key to at least read its own transaction
                    # results.
                    print("         - WARNING: User has insuficient rights to read own transaction")
                    print(json.dumps(transaction, indent=4, sort_keys=True))
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
                if "_tx/error" in status[0]:
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
    response = list()
    for obj in response0:
        if "_id" in obj:
            del obj["_id"]
        if obj:
            response.append(obj)
    if response0 and not response:
        print("        - NOTE: Non-empty response treated as functionally empty (only _id fields)")
    # On success we expect a non-empty result
    if succeed and len(response) == 0:
        print("Empty response on YES query")
        print(json.dumps(query, indent=4, sort_keys=True))
        raise RuntimeError("Empty response to YES query.")
    # On failure we expect an empty result
    if not succeed and response:
        print("Non-empty response on NO query")
        print(json.dumps(query, indent=4, sort_keys=True))
        print(json.dumps(response, indent=4, sort_keys=True))
        raise RuntimeError("Non-empty response to NO query.")
