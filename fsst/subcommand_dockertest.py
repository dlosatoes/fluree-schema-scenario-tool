import asyncio
from fsst.docker_utils import run_in_docker

async def dockertest_main(directory, target, verboseerrors, network, tag, verbosefluree, linger, persistent):
    """Main function for the dockertest subcommand"""
    if persistent is not None:
        print("Warning: commandline argument is ignored: 'persistent'")
    # pylint: disable=too-many-arguments
    cmd = "./fsst guesttest --target " + target + " --network " + network
    if verboseerrors:
        cmd += " --verboseerrors"
    if verbosefluree:
        cmd += " --verbosefluree"
    if linger:
        cmd += " --linger"
    return run_in_docker(tag, cmd, directory, False, linger)
