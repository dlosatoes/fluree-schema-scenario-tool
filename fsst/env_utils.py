import sys
import subprocess
import hashlib
try:
    import base58
except ModuleNotFoundError:
    pass
try:
    import bitcoinlib
except ModuleNotFoundError:
    pass

from fsst.docker_utils import get_from_docker

def runs_in_docker():
    """Check if we are running inside of docker"""
    try:
        with open("/proc/1/cgroup") as cgrp:
            # Read the cgroup file if on Linux
            cgrplines = cgrp.read().split("\n")[:-1]
            # Count the occurences of "/", should only be one or two when in docker.
            cnt = [line.split(":")[2] for line in cgrplines].count("/")
        if cnt < 3:
            return True
    except FileNotFoundError:
        pass
    return False

def key_to_id(privkey):
    """Convert a private key string into a fluree account id.

    Parameters
    ----------
    privkey: string
        A hexadecimal ECDSA private key.

    Returns
    -------
    str
        Base58 encoded adress/key-id within the FlureeDB address namespace

    """
    if privkey:
        # Remove the bitcoin network id and the checksum from the base58 decoded bitcoin adress,
        # then prefix with fluree network id.
        core = b'\x0f\x02' + base58.b58decode(bitcoinlib.keys.Key(privkey).address())[1:-4]
        # Take the sha256 of the sha256 of the decoded and patched bitcoin adress.
        hash1 = hashlib.sha256()
        hash2 = hashlib.sha256()
        hash1.update(core)
        hash2.update(hash1.digest())
        # Use the first 4 characters as checksum, base58 encode the result.
        keyid = base58.b58encode(core + hash2.digest()[:4]).decode()
        return keyid
    return None

async def get_createkey_and_port(createkey, keyfile, dockerfind, port, startfluree, verbosefluree):
    """Get the create-key and fluree port using the relevant commandline info"""
    # pylint: disable=too-many-arguments
    if startfluree:
        rval = None
        command = ["/bin/bash", "/usr/src/fsst/fluree_start.sh"]
        if not verbosefluree:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(command)
        times = 0
        while not rval:
            try:
                with open("./default-private-key.txt") as kfile:
                    rval = kfile.read()
            except FileNotFoundError:
                print("# waiting for default-private-key.txt to appear")
            await asyncio.sleep(6)
            times += 1
            if times > 40:
                print("ERROR: Taking too long for default-private-key.txt to apear in docker")
                print("       container after starting FlureeDB")
                sys.exit(1)
        print("Started FlureeDB and got createkey from newly created keyfile")
        return rval, port, key_to_id(rval)
    if createkey:
        print("Using --createkey and --port values", )
        return createkey, port, key_to_id(createkey)
    if keyfile:
        print("Using --keyfile and --port values")
        with open(keyfile) as kfil:
            createkey = kfil.read().replace("\r", "").replace("\n", "")
            return createkey, port, key_to_id(createkey)
    if dockerfind:
        print("Fetching createkey and port from running image:", dockerfind)
        hostport, createkey = get_from_docker(dockerfind)
        return createkey, hostport, key_to_id(createkey)
    print("ERROR: No way specfied to find default signing key for FlureeDB")
    print("       Use one of the following command line options:")
    print("")
    print("         --createkey")
    print("         --keyfile")
    print("         --dockerfind")
    sys.exit(1)
