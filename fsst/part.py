import os
import hashlib
import json
import copy
import shutil
import yaml

def file_hash(path):
    with open(path) as jsonfile:
        if path.split(".")[-1].lower() == "json":
            data = json.dumps(json.load(jsonfile), sort_keys=True)
        else:
            data = jsonfile.read()
        blkhash = hashlib.blake2b(digest_size=32)
        blkhash.update(data.encode())
        return blkhash.hexdigest()

def get_source_paths(partdir, maincontent):
    for transaction in maincontent:
        for operation in transaction:
            if "code_expand" in operation:
                yield operation["code_expand"]

def get_sources(partdir, mainpath, mainbody):
    rval = dict()
    rval["hashes"] = dict()
    rval["hashes"][os.path.basename(mainpath)] = file_hash(mainpath)
    for subpath in get_source_paths(partdir, mainbody):
        rval["hashes"][subpath] = file_hash(os.path.join(partdir, subpath))
    rval["transaction_count"] = len(mainbody)
    return rval

def main_generator(dir_path, alt_file):
    num = 0
    cont = True
    if alt_file is not None:
        yield alt_file
        cont = False
    while cont:
        num += 1
        filename = "main-" + str(num).zfill(6) + ".json"
        path = os.path.join(dir_path, filename)
        if os.path.isfile(path):
            yield path
        elif num == 1:
            path = os.path.join(dir_path, "main.json")
            if os.path.isfile(path):
                yield path
            else:
                cont = False
        else:
            cont = False

def get_mains_data(dir_path, file_path):
    rval = list()
    for filepath in main_generator(dir_path, file_path):
        with open(filepath) as mainfile:
            transactions = json.load(mainfile)
            rval.append(get_sources(dir_path, filepath, transactions))
    return rval

class Version:
    def __init__(self, vname, vobj, isfile):
        self.vname = vname
        if "depends_on" in vobj:
           self.depends_on = vobj["depends_on"]
        else:
            self.depends_on = []
        if "transaction_count" in vobj:
            self.transaction_count = vobj["transaction_count"]
        else:
            self.transaction_count = 0
        if "frozen_deps" in vobj:
            self.frozen_deps = vobj["frozen_deps"]
        else:
            self.frozen_deps = False
        hashes = vobj["hashes"]
        self.mainfile = "OOPS"
        for key in hashes.keys():
            if (isfile or key[:4] == "main") and key[-5:] == ".json":
                self.mainfile = key
            else:
                print("skip:", key, key[:4] == "main", key[-5:] == ".json")
    def __str__(self):
        return self.vname + " " + str(self.depends_on) + " " + str(self.transaction_count) + " " + str(self.frozen_deps) + " " +  self.mainfile



class PartDir:
    def __init__(self, flureedir, part):
        self.flureedir = flureedir
        self.part = part
        if not os.path.isdir(flureedir):
            raise RuntimeError("Invalid fluree_parts dir : " + flureedir)
        lockdir_path = os.path.normpath(flureedir) + "-lock"
        if not os.path.isdir(lockdir_path):
            os.mkdir(lockdir_path)
        lock_path = os.path.join(lockdir_path, part + "-part.json")
        file_path = os.path.join(flureedir, part + ".json")
        dir_path  = os.path.join(flureedir, part)
        deps_path = os.path.join(flureedir, part, "deps.yml")
        haslockfile = os.path.isfile(lock_path)
        hasfile = os.path.isfile(file_path)
        hasdir = os.path.isdir(dir_path)
        hasdeps = os.path.isfile(deps_path)
        if (haslockfile and (not hasdir)):
            raise RuntimeError("Build-part that has a lockfile must have a subdir")
        if (hasfile and hasdir):
            raise RuntimeError("Build-part can't have both a file and a subdir")
        if (not (hasfile or hasdir)):
            raise RuntimeError("Invalid build-part")
        self.isfile = hasfile
        self.latest_deps = dict()
        self.latest_lock = dict()
        self.lock_path = None
        self.file_path = None
        self.dir_path = None
        self.deps_path = None
        if hasdeps:
            self.deps_path = deps_path
            with open(deps_path) as infil:
                yml = infil.read()
            self.latest_deps = yaml.load(yml, Loader=yaml.FullLoader)
        else:
            self.latest_deps = {"depends_on": [], "defer_tests": []}
        if haslockfile:
            self.lock_path = lock_path
            with open(lock_path) as infil2:
                self.latest_lock = json.load(infil2)
        else:
            self.lock_path = lock_path
            self.latest_lock = dict()
        if hasfile:
            self.file_path = file_path
            self.dir_path = dir_path
        else:
            self.dir_path = dir_path
        if hasfile:
            self.mains = get_mains_data(self.dir_path, file_path)
        else:
            self.mains = get_mains_data(self.dir_path, None)
        for index in range(1,len(self.latest_lock)):
            vstring = "v"+str(index).zfill(6)
            frozen_hashes = self.latest_lock[vstring]["hashes"]
            active_hashes = self.mains[index]["hashes"]
            if set(frozen_hashes.keys()).symmetric_difference(set(active_hashes.keys())):
                raise RuntimeError("Integrity error for version " + vstring + ", non-matching file-hash keys")
            for key in frozen_hashes.keys():
                if frozen_hashes[key] != active_hashes[key]:
                    raise RuntimeError("Integrity error for version " + vstring + ", frozen version file " + key + " has changed") 
        self.latest_deps["hashes"] = self.mains[-1]["hashes"]
        self.latest_deps["transaction_count"] = self.mains[-1]["transaction_count"]
        self.frozen = self.mains[-1]["transaction_count"] == 0
    def file_to_dir(self):
        if not self.isfile:
            raise RuntimeError("Trying to migrate to dir based part without a file to migrate")
        os.mkdir(self.dir_path)
        newpath = os.path.join(self.dir_path,"main.json")
        shutil.move(self.file_path, newpath)
        return PartDir(self.flureedir, self.part)
    def freeze(self):
        if self.frozen:
            raise RuntimeError("No new transactions since last freeze")
        if self.isfile:
            return self.file_to_dir().freeze()
        newnum = len(self.mains)
        vstring = "v" + str(newnum).zfill(6)
        newnum += 1
        mainfil = os.path.join(self.dir_path, "main-" + str(newnum).zfill(6) + ".json")
        self.latest_lock[vstring] = copy.deepcopy(self.latest_deps)
        self.latest_lock[vstring]["frozen_deps"] = True
        self.latest_deps["hashes"] = dict()
        self.latest_deps["transaction_count"] = 0
        self.frozen = True
        with open(mainfil,"w") as newfil:
            newfil.write("[]")
        with open(self.lock_path,"w") as lockfile:
            json.dump(self.latest_lock, lockfile)
    def unfreeze_deps(self):
        unfrozen = dict()
        newnum = len(self.mains)
        vstring = "v" + str(newnum).zfill(6)
        unfrozen[vstring] = dict()
        if "depends_on" in self.latest_deps:
            unfrozen[vstring]["depends_on"] = self.latest_deps["depends_on"]
        else:
            unfrozen[vstring]["depends_on"] = []
        if "defer_tests" in self.latest_deps:
            unfrozen[vstring]["defer_tests"] = self.latest_deps["defer_tests"]
        else:
            unfrozen[vstring]["defer_tests"] = []
        for key in self.latest_lock.keys():
             unfrozen[key] = dict()
             unfrozen[key]["depends_on"] = self.latest_lock[key]["depends_on"]
             unfrozen[key]["defer_tests"] = self.latest_lock[key]["defer_tests"]
        serialized = yaml.dump(unfrozen)
        un_file = os.path.join(self.dir_path, "unfrozen_deps.yml")
        with open(un_file,"w") as outfil:
            outfil.write(serialized)
        return un_file
    def refreeze_deps(self):
        un_file = os.path.join(self.dir_path, "unfrozen_deps.yml")
        with open(un_file) as infil:
            yml = infil.read()
        unfrozen = yaml.load(yml, Loader=yaml.FullLoader)
        newnum = len(self.mains)
        vstring = "v" + str(newnum).zfill(6)
        mypart = unfrozen.pop(vstring)
        for key in unfrozen:
            self.latest_lock[key]["depends_on"] = unfrozen[key]["depends_on"]
            self.latest_lock[key]["defer_tests"] = unfrozen[key]["defer_tests"]
        with open(self.lock_path,"w") as lockfile:
            json.dump(self.latest_lock, lockfile)
        buildfile = os.path.join(self.dir_path, "deps.yml")
        serialized = yaml.dump(mypart)
        with open(buildfile,"w") as bfile:
            bfile.write(serialized)
        os.remove(un_file)
    def max_version(self):
        keys = self.latest_lock.keys()
        maxnum = 0
        version = "beta"
        if keys:
            for key in keys:
                print(key)
                num = int(key[1:])
                if num > maxnum:
                    version = key
                    maxnum = num
        return version
    def get_version(self, version):
        if version == "beta":
            return Version("beta", self.latest_deps, self.isfile)
        return Version(version, self.latest_lock[version], self.isfile)
    def get_latest(self):
        return self.get_version(self.max_version())
    def get_beta(self):
        return self.get_version("beta")

pd = PartDir("../fluree_parts", "there_can_be_only_one")
print()
print(pd.get_latest())
print()
print(pd.get_beta())

pd = PartDir("../fluree_parts", "roles")
print()
print(pd.get_latest())
print()
print(pd.get_beta())

pd.freeze()
#pd.unfreeze_deps()
#pd.refreeze_deps()
