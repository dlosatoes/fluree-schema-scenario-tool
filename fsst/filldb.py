import asyncio
import json
import aioflureedb

async def filldb(host, port, dbase, key, keyid, transactions):
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
    keyid: string
        The key-id of the above signing key
    transactions: list
        A list with Fluree transactions to execute.

    Raises
    ------
    aioflureedb.FlureeException
        If schema transaction is invalid

    """
    # pylint: disable=too-many-arguments
    async with  aioflureedb.FlureeClient(masterkey=key,
                                         auth_address=keyid,
                                         host=host,
                                         port=port) as flureeclient:
        await flureeclient.health.ready()
        await flureeclient.new_db(db_id=dbase)
        fdb = await flureeclient[dbase]
        async with fdb(key, keyid) as database:
            await database.ready()
            for transaction in transactions:
                try:
                    await database.command.transaction(transaction)
                except aioflureedb.FlureeException as exp:
                    print("Exception while processing schema transaction")
                    print(json.dumps(transaction, indent=4, sort_keys=True))
                    print()
                    raise exp
