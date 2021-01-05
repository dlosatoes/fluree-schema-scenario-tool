import asyncio
from fsst.docker_utils import run_in_docker


async def dockerdeploy_main(directory, target, verboseerrors, dbase, tag, verbosefluree, daemonize, targetversion, nondeploy, persistent):
    """Main function for the dockerdeploy subcommand"""
    if targetversion is not None:
       print("WARNING: commandline option ignored: 'targetversion'")
    if nondeploy:
       print("WARNING: commandline option ignored: 'nondeploy'")
    if persistent is not None:
       print("WARNING: commandline option ignored: 'persistent'")
    # pylint: disable=too-many-arguments
    cmd = "./fsst guestdeploy " + dbase + " --target " + target + \
            " --linger"
    if verboseerrors:
        cmd += " --verboseerrors"
    if verbosefluree or not daemonize:
        cmd += " --verbosefluree"
    return run_in_docker(tag, cmd, directory, daemonize, True)

