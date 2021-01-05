import os
import sys
import webbrowser
try:
    import docker
except ModuleNotFoundError:
    pass

def get_running_docker(client, tag):
    """Get the running docker"""
    name = "pibara/fsst:" + tag
    for container in client.containers.list():
        for ttag in  container.image.attrs["RepoTags"]:
            if ttag == name:
                return container
    return None

def get_container_info(container):
    """Get host port and create key from docker"""
    hostport = None
    createkey = None
    if ("HostConfig" in container.attrs and
            "PortBindings" in container.attrs["HostConfig"] and
            "8080/tcp" in container.attrs["HostConfig"]["PortBindings"]):
        for binding in container.attrs["HostConfig"]["PortBindings"]["8080/tcp"]:
            if "HostPort" in binding:
                hostport = binding["HostPort"]
    command_result = container.exec_run("cat default-private-key.txt")
    if command_result.exit_code == 0:
        createkey = command_result.output.decode()
    return hostport, createkey

def get_from_docker(tag):
    """Retreive the host port and the createkey from a running fsst docker image"""
    client = docker.from_env()
    container = get_running_docker(client, tag)
    if not container:
        print("ERROR: Running docker with tag", tag, "not found")
        sys.exit(1)
    hostport, createkey = get_container_info(container)
    return hostport, createkey

def run_in_docker(tag, command, directory, daemonize, expose):
    """Run a given command in a new docker container"""
    # pylint: disable=too-many-locals
    print("COMMAND:", command)
    match = None
    lookfor = "pibara/fsst:" + tag
    print("IMAGE:", lookfor)
    client = docker.from_env()
    for image in client.images.list():
        for repotag in image.attrs["RepoTags"]:
            if repotag == lookfor:
                match = image
    if match is None:
        print("ERROR: ", lookfor, "docker image not found")
        sys.exit(0)
    workdir = os.path.join(os.getcwd(), directory)
    if not os.path.isdir(workdir):
        print("ERROR:", workdir, "isn't a valid directory path")
        sys.exit(1)
    mount = docker.types.Mount("/usr/src/fsst/fluree_parts", workdir, read_only=True, type="bind")
    ports = dict()
    name = "fsst-guestcommand-" + tag
    if expose or daemonize:
        ports["8080/tcp"] = 8090
    try:
        container = client.containers.run(match, command, mounts=[mount], ports=ports, detach=True, auto_remove=True, name=name)
    except docker.errors.APIError as exp:
        print("ERROR: Problem starting docker container OR issue binding to 8090")
        print(exp)
        sys.exit(1)
    try:
        browser_triggered = False
        runcmd = container.logs(stream=True, follow=True)
        if daemonize:
            print("Starting fluree, waiting for fluree to initialize before daemonizing")
            print("Browser should start up, shortly")
        for line in runcmd:
            sline = line.decode().replace("\r", "").replace("\n", "")
            if not daemonize:
                print(sline, flush=True)
            if sline == "LINGER == True" and browser_triggered is False:
                webbrowser.open("http://localhost:8090/")
                browser_triggered = True
                if daemonize:
                    runcmd.close()
                    break
    except KeyboardInterrupt:
        print("Stopping container")
        container.stop()
        print("Container stopped after keyboard interrupt")


