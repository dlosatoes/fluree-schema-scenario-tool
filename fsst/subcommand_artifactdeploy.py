import asyncio
import json
import sys
try:
    import aioflureedb
except ModuleNotFoundError:
    pass

async def artifactdeploy_main(inputfile, dbase, host, port, createkey, keyid, targetversion, upgrade):
    # pylint: disable=too-many-arguments
    """Main function for the artifactdeploy subcommand"""
    if upgrade is not None:
        print("WARNING: ignored commandline parameter 'upgrade'")
    if targetversion is not None:
        print("WARNING: ignored commandline parameter 'targetversion'")
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
    async with  aioflureedb.FlureeClient(masterkey=createkey,
                                         auth_address=keyid,
                                         host=host,
                                         port=port) as flureeclient:
        await flureeclient.health.ready()
        # Create the new database for our tests
        try:
            await flureeclient.new_db(db_id=dbase)
        except aioflureedb.FlureeHttpError as exp:
            print("ERROR: Problem creating the database for deploy")
            print("      ", json.loads(exp.args[0])["message"])
            sys.exit(1)
        fdb = await flureeclient[dbase]
        # Database context
        async with fdb(createkey, keyid) as database:
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

