import asyncio
from fsst.refactor_me import fluree_main

async def deploy_main(directory, target, verboseerrors, host, port, network, createkey, createid, targetversion, nondeploy, upgrade):
    """Main function for the deploy subcommand"""
    # pylint: disable=too-many-arguments
    if targetversion is not None:
        print("WARING: ignored commandline option 'targetversion'")
    if nondeploy:
        print("WARING: ignored commandline option 'nondeploy'")
    if upgrade is not None:
        print("WARING: ignored commandline option 'upgrade'")
    await fluree_main(notest=True,
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


