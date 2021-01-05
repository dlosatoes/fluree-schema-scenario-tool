from fsst.docker_utils import get_running_docker
try:
    import docker
except ModuleNotFoundError:
    pass

async def dockerstop_main(tag):
    """Main function for the dockerstop subcommand"""
    lookfor = "pibara/fsst:" + tag
    client = docker.from_env()
    container = get_running_docker(client, tag)
    if container:
        container.stop()
        print("Stopping", lookfor)
    else:
        print("ERROR: no running instance of", lookfor, "found")
