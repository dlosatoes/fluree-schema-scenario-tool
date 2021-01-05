import fsst
import asyncio
try:
    import docker
except ModuleNotFoundError:
    pass

async def versioncheck_main(tag):
    """Main function for the versioncheck subcommand"""
    # pylint: disable=too-many-branches
    match = None
    lookfor = "pibara/fsst:" + tag
    client = docker.from_env()
    for image in client.images.list():
        for repotag in image.attrs["RepoTags"]:
            if repotag == lookfor:
                match = image
    if match is None:
        print("ERROR: ", lookfor, "docker image not found")
        sys.exit(0)
    cmd = "./fsst version"
    name = "fsst-versioncheck-" + tag
    try:
        container = client.containers.run(match, cmd, detach=False, auto_remove=True, name=name)
    except docker.errors.ContainerError:
        print("ERROR: Container Error.")
        print("       This might be the result of a 0.1.x version of the docker container")
        print("       that didn't support --version yet")
        sys.exit(1)
    dockerfsstversion = None
    for line in container.decode().split("\n"):
        parts = line.split(":")
        if len(parts) == 2 and parts[0] == "FSST VERSION":
            dockerfsstversion = parts[1].replace(" ", "")
            dockerfsst = dockerfsstversion.split(".")
    if not dockerfsstversion:
        print("ERROR: No valid response to --version from fsst in docker.")
        print("       This might be the result of a 0.1.x version of the docker container")
        print("       that didn't support --version yet")
        sys.exit(1)
    localfsst = fsst.VERSION.split(".")
    if dockerfsst[0] == localfsst[0]:
        if dockerfsst[1] == localfsst[1]:
            if dockerfsst[2] == localfsst[2]:
                print("Perfect version match:", fsst.VERSION, "for image", lookfor)
            else:
                print("Near version match:", fsst.VERSION, "local vs", dockerfsstversion,
                      "in docker image", lookfor, ". Should be OK.")
        else:
            print("NOTICE: Possible version mismatch:", fsst.VERSION, "local vs", dockerfsstversion,
                  "in docker image", lookfor, "Use with care.")
    else:
        print("WARNING: Version mismatch:", fsst.VERSION, "local vs", parts[1], "in docker image",
              lookfor)
        sys.exit(1)
    return

