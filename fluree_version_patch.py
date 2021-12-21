#!/usr/bin/python3
from pyparsing import nestedExpr, LineEnd

VERSION = "0.4.1"

def remove_comments(data):
    rval = list()
    for line in data.split("\n"):
        if ";;" in line:
            line = line.split(";;")[0]
        rval.append(line)
    return "\n".join(rval)

def reconstruct(rlist, indent=0):
    indent_string = " "*indent*4
    long_indent_string = " "*(indent+1)*4
    rval = "{"
    first = True
    is_ledger = False
    patch_next = False
    for subval in rlist:
        if isinstance(subval, str):
            if patch_next:
                subval = subval[:-1] + "-fsst-" + VERSION + subval[-1:]
            patch_next = False
            if subval == "ledger":
                is_ledger = True
            if is_ledger and subval == ":mvn/version":
                patch_next = True
            if subval[0] == ":" :
                if rval[-1] == "{" or first:
                    rval += subval
                else:
                    rval += "\n" + indent_string + "    " + subval
            else:
                if rval[-1] == "}":
                    rval += "\n" + indent_string + "    " + subval
                else:
                    rval += " " + subval + " "
                if subval[0:2] == ";;":
                    rval += "\n" + indent_string + "    "
        else:
            patch_next = False
            if not first:
                rval += " "
            rval += reconstruct(subval, indent + 1)
        first = False
    rval += "}"
    return rval

with open("deps.edn") as deps_file:
    data = deps_file.read()
data = remove_comments(data)
out = reconstruct(nestedExpr('{','}').parseString(data).asList()[0])
with open("deps.edn","w") as deps_file:
    deps_file.write(out)
