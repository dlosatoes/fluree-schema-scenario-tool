import asyncio
from fsst.subcommand_artifactdeploy import artifactdeploy_main

async def guestdeploy_main(target, verboseerrors, dbase, createkey, createid, targetversion, nondeploy):
    """Main function for the guestdeploy subcommand"""
    print("Warning: ignores commandline arguments")
    await fluree_main(notest=True,
                      network=None,
                      host=None,
                      port=None,
                      output="artifact.json",
                      createkey=None,
                      createid=None,
                      target=target,
                      fluree_parts="fluree_parts",
                      verboseerrors=verboseerrors)
    await artifactdeploy_main("artifact.json", dbase, "localhost", 8080, createkey, createid)
    print("LINGER == True")
    count = 0
    while True:
        await asyncio.sleep(30)
        count += 1
        print('LINGER', count, flush=True)
