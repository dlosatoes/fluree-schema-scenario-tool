import asyncio
from fsst.refactor_me import fluree_main

async def artifact_main(output, directory, target, verbose_errors, beta, targetversion, nondeploy, allversions):
    """Main function for the artifact sub command"""
    if beta:
        print("WARNING: ignored commandline arguments 'beta'")
    if targetversion is not None:
        print("WARNING: ignored commandline arguments 'targetversion'")
    if nondeploy:
        print("WARNING: ignored commandline arguments 'nondeploy'")
    if allversions:
        print("WARNING: ignored commandline arguments 'allversions'")
    await fluree_main(notest=False,
                      network=None,
                      host=None,
                      port=None,
                      output=output,
                      createkey=None,
                      createid=None,
                      target=target,
                      fluree_parts=directory,
                      verboseerrors=verbose_errors,
                      )
    return
