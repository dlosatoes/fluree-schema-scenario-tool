import asyncio
from fsst.refactor_me import fluree_main

async def guesttest_main(target, verboseerrors, network, linger, createkey, createid):
    """Main function for the guesttest subcommand"""
    # pylint: disable=too-many-arguments
    await fluree_main(notest=False,
                      network=network,
                      host="localhost",
                      port=8080,
                      output=None,
                      createkey=createkey,
                      createid=createid,
                      target=target,
                      fluree_parts="fluree_parts",
                      verboseerrors=verboseerrors)
    if linger:
        print("LINGER == True")
        count = 0
        while True:
            await asyncio.sleep(30)
            count += 1
            print('LINGER', count, flush=True)
    return
