try:
    import docker
except ModuleNotFoundError:
    pass

async def dockerstart_main(tag, persistent):
    """Main function for the dockerstart subcommand"""
    if persistent is not None:
        print("WARNING: Commandline argument ignored: 'persistent'")
    imagename = "pibara/fsst:" + tag
    command = "/bin/bash /usr/src/fsst/fluree_start.sh"
    ports = dict()
    ports["8080/tcp"] = 8090
    client = docker.from_env()
    name = "fsst-dockerstart-" + tag
    try:
        client.containers.run(imagename, command, ports=ports, detach=True, auto_remove=True, name=name)
        print("Started", imagename)
    except docker.errors.NotFound:
        print("ERROR:", imagename, "not found")
    return

