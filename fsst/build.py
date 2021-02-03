import os
import json
import shutil
import yaml
from part import PartDir

def deps_if_no_deps(flureedir, part, prevpart):
    partfile = os.path.join(flureedir, part + ".json")
    partdir = os.path.join(flureedir, part)
    if os.path.isfile(partfile):
        if os.path.isdir(partdir):
            raise RuntimeError("Found both a part dir and a part file for " + part)
        else:
            os.mkdir(partdir)
            newpath = os.path.join(partdir,"main.json")
            shutil.move(partfile, newpath)
    if not os.path.isdir(partdir):
        raise RuntimeError("No such part found :", part)
    depsfile = os.path.join(partdir, "deps.yml")
    if os.path.isfile(depsfile):
        with open(depsfile) as infil:
            yml = infil.read()
        latest_deps = yaml.load(yml, Loader=yaml.FullLoader)
    else:
        latest_deps = dict()
        latest_deps["depends_on"] = list()
    founddep = False
    for deps in latest_deps["depends_on"]:
        if (len(deps.keys()) == 1) and (prevpart in deps):
            founddep = True
    if not founddep:
        latest_deps["depends_on"].append(dict())
        latest_deps["depends_on"][-1][prevpart] = dict()
    serialized = yaml.dump(latest_deps)
    with open(depsfile,"w") as dfile:
        dfile.write(serialized)


def migrate_json_to_yaml(jsonbuildpath, yamlbuildpath, flureedir):
    with open(jsonbuildpath) as jsonfile:
        obj = json.load(jsonfile)
    result = dict()
    prevkey = None
    for target in obj.keys():
        result[target] = [{}]
        prevpart = None
        for part in obj[target]:
            result[target][0][part] = dict()
            if prevpart is not None:
                deps_if_no_deps(flureedir, part, prevpart)
            prevpart = part
        prevpart = part
    serialized = yaml.dump(result)
    with open(yamlbuildpath, "w") as outfil:
        outfil.write(serialized)

class Build:
    def __init__(self, flureedir, target):
        self.flureedir = flureedir
        oldbuildfile_path = os.path.join(flureedir,"build.json")
        self.buildfile_path =  os.path.join(flureedir,"build.yml")
        if not os.path.isfile(self.buildfile_path):
            if os.path.isfile(oldbuildfile_path):
                migrate_json_to_yaml(oldbuildfile_path, self.buildfile_path, flureedir)
            else:
                raise RuntimeError("No build.yml file found in " + flureedir)
        with open(self.buildfile_path) as buildfile:
            yml = buildfile.read()
        self.build_info = yaml.load(yml, Loader=yaml.FullLoader)
        if target not in self.build_info:
            raise RuntimeError("Build target '" + target + "' not found in " + self.buildfile_path)
        self.targetbuild = self.build_info[target]
        print(self.targetbuild)
        self.parts = dict()
        for candidate in self.targetbuild:
            for part in candidate.keys():
                if part not in self.parts:
                    self.parts[part] = dict()
                    self.parts[part]["obj"] = PartDir(flureedir, part)
                    self.parts[part]["deps"] = self.parts[part]["obj"].latest_deps
                    self.parts[part]["lock"] = self.parts[part]["obj"].latest_lock
        print(self.buildfile_path)
        print()
        print(self.parts)

build = Build("../fluree_parts", "default")
