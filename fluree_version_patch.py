#!/usr/bin/python3
from pyparsing import nestedExpr, LineEnd

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
    for subval in rlist:
        if isinstance(subval, str):
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
print(out)
