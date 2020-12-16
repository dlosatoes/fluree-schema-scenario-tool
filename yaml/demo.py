#!/usr/bin/python3
import json
import yaml

def undiff(version, old_version):
    if not old_version:
        return version
    rval = dict()
    for stage in old_version:
        rval[stage] = dict()
        for key in old_version[stage]:
            rval[stage][key] = old_version[stage][key]
    auto_order = 10000
    for stage in version:
        if stage not in rval:
            rval[stage] = dict()
            rval[stage]["order"] = auto_order
            auto_order += 1
        for key in version[stage]:
            rval[stage][key] = version[stage][key]
    return rval

def make_order_proposal(version):
    auto_order = 123456
    ordermap = dict()
    for key in version:
        if "order" in version[key] and not version[key]["order"] in ordermap:
            ordermap[version[key]["order"]] = key
        else:
            ordermap[auto_order] = key
            auto_order += 1
    orderkeys = list(ordermap.keys())
    orderkeys.sort()
    rval = list()
    for order in orderkeys:
        rval.append(ordermap[order])
    return rval

def version_add_version(version):
    for key in version:
        if version[key] == None:
            version[key] = dict()
        if "version" not in version[key]:
            version[key]["version"] = 1
    return version

def version_add_order(version, old_version):
    if old_version:
        version = undiff(version, old_version)
        order_proposal = make_order_proposal(version)
    else:
        order_proposal = list(version.keys())
    version = version_add_version(version)
    progress = True
    output = list()
    output2 = list()
    while progress and version:
        progress = False
        for key in order_proposal:
            if not progress:
                obj = version[key]
                move = True
                if obj is not None and "depends_on" in obj:
                    for dependency in obj["depends_on"]:
                        if dependency in version:
                            move = False
                if move:
                    progress = True
                    remove = key
                    output.append(key)
                    output2.append(obj)
                    del(version[key])
        if progress:
            order_proposal.remove(remove)
    if version:
        raise RuntimeError("Unresolvable dependencies")
    rval = dict()
    order = 1
    for i in range(0, len(output)):
        if output2[i] is None:
            output2[i] = dict()
        output2[i]["order"] = order
        order += 1
        rval[output[i]] = output2[i]
    return rval

def target_add_order(target):
    old_version = dict()
    rval = list()
    for version in target:
        rval.append(version_add_order(version, old_version))
        old_version = rval[-1]
    for i in range(0, len(rval)-1):
        for stage in rval[i]:
            if "depends_on" in rval[i][stage]:
                del(rval[i][stage]["depends_on"])
            if "defer_tests" in rval[i][stage]:
                del(rval[i][stage]["defer_tests"])
    return rval

def all_add_order(all_targets):
    rval = dict()
    for key in all_targets.keys():
        rval[key] = target_add_order(all_targets[key])
    return rval

with open("build.yml") as infil:
    yml = infil.read()
    demo_in = yaml.load(yml, Loader=yaml.FullLoader)

result = all_add_order(demo_in)
print(json.dumps(result))


