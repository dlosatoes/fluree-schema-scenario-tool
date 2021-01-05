import asyncio
try:
    import docker
except ModuleNotFoundError:
    pass
from fsst.docker_utils import get_running_docker

async def dockerparams_main(tag):
    """Main function for the dockerparams subcommand"""
    client = docker.from_env()
    container = get_running_docker(client, tag)
    if container is None:
        print("ERROR, running container not found for tag =", tag)
        return
    echo = container.exec_run("cat default-private-key.txt")
    createkey = None
    port = None
    if echo.exit_code == 0:
        createkey = echo.output.decode()
    if ("HostConfig" in container.attrs and
            "PortBindings" in container.attrs["HostConfig"] and
            "8080/tcp" in container.attrs["HostConfig"]["PortBindings"] and
            container.attrs["HostConfig"]["PortBindings"]["8080/tcp"]):
        for binding in container.attrs["HostConfig"]["PortBindings"]["8080/tcp"]:
            if "HostPort" in binding:
                port = int(binding["HostPort"])
    print("IMAGE:", tag)
    print("CREATEKEY:", createkey)
    print("PORT:", port)
