import asyncio
from fsst.refactor_me import fluree_main

async def test_main(directory, target, verboseerrors, host, port, network, createkey, createid):
    """Main function for the test subcommand"""
    # pylint: disable=too-many-arguments
    await fluree_main(notest=False,
                      network=network,
                      host=host,
                      port=port,
                      output=None,
                      createkey=createkey,
                      createid=createid,
                      target=target,
                      fluree_parts=directory,
                      verboseerrors=verboseerrors)
    return
