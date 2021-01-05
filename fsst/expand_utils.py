import json
import re
import copy
import itertools

def query_to_clojure(obj, params):
    """Convert a FlureeQL query to a clojure '(query (str ...) )' smart-function function body.

    Parameters
    ----------
    obj: dict
        Dict object containing a FlureeQL query
    params: list
        List of parameters to insert into clojure expression

    Returns
    -------
    str
        A clojure (str ) expression that builds the param substituted FlureeQL query as a string.

    Raises
    ------
    RuntimeError
        If PARAM count in JSON and params length don't match
    """
    # Serialize the query, sorted keys for deterministic substitution, no pretty printing
    data = json.dumps(obj, sort_keys=True)
    # Split the JSON into parts using 'PARAM' as seperator
    parts = data.split("PARAM")
    # Escape each JSON part by serializing as a JSON list and removing the qruare brackets
    escaped_parts = [json.dumps([part])[1:-1] for part in parts]
    # The amount of parts should be one more than the amount ot parameters
    if len(parts) != len(params) + 1:
        raise RuntimeError("Param count mismatch: " +
                           str(len(params)) +
                           " given " +
                           str(len(parts) -1) +
                           " needed ; " +
                           data)
    # Interleave the escaped JSON parts and the parameters and put them in a (str ) clojure
    #  expression
    rval = " ".join(list(itertools.chain(*zip(["(query (str "] + params, escaped_parts))) + [") )"])
    return rval

def query_to_clojure_previous(obj, params):
    """Convert a FlureeQL query to a clojure '(query (str ...) )' smart-function function body.

    Parameters
    ----------
    obj: dict
        Dict object containing a FlureeQL query
    params: list
        List of parameters to insert into clojure expression

    Returns
    -------
    str
        A clojure (str ) expression that builds the param substituted FlureeQL query as a string.

    Raises
    ------
    RuntimeError
        If PARAM count in JSON and params length don't match
    """
    # Serialize the query, sorted keys for deterministic substitution, no pretty printing
    obj["block"] = 1234567890987 #magic number
    data = json.dumps(obj, sort_keys=True)
    # Split the JSON into parts using 'PARAM' as seperator
    parts = data.split("PARAM")
    # Escape each JSON part by serializing as a JSON list and removing the qruare brackets
    escaped_parts = [json.dumps([part])[1:-1] for part in parts]
    # The amount of parts should be one more than the amount ot parameters
    if len(parts) != len(params) + 1:
        raise RuntimeError("Param count mismatch: " +
                           str(len(params)) +
                           " given " +
                           str(len(parts) -1) +
                           " needed ; " +
                           data)
    # Interleave the escaped JSON parts and the parameters and put them in a (str ) clojure
    #  expression
    rval = " ".join(list(itertools.chain(*zip(["(query (str "] + params, escaped_parts))) + [") )"])
    # Now do the same with our magic number
    parts = rval.split(str(obj["block"]))
    if len(parts) != 2:
        raise RuntimeError("Problem with block insertion query_to_clojure_previous")
    return parts[0] + '" (query lastBlock) "' + parts[1]

def expand_operation(operation, subdir, fluree_parts, verboseerrors):
    """Expand any "code_expand" or "code+from_query" in a single operation within a transaction

    Parameters
    ----------
    operation: dict
        FlureeQL operation object taken from within a transaction
    subdir: str
        Component directory name
    fluree_parts: str
        Fluree build sources top dir directory path
    verboseerrors: boolean
        Add extra errpr message to rules that don't define them
    Returns
    -------
    str
        Potentially expanded version of the supplied operation
    """
    # If the operation has a "params" field, use it, otherwise use empty list.
    params = []
    if (verboseerrors and "_id" in operation and "id" in operation
            and operation["_id"].startswith("_rule")
            and "errorMessage" not in operation):
        print("Adding verbose error for", operation["id"])
        operation["errorMessage"] = "Verbose Errors: " + operation["id"]
    if "params" in operation:
        params = operation["params"]
    if "code_expand" in operation:
        # Read the file designated in the code_expand field
        path = fluree_parts + "/" + subdir + "/" + operation["code_expand"]
        with open(path) as datafile:
            data = datafile.read()
            data = re.sub(' +', ' ', data.replace("\n"," "))
        if operation["code_expand"].split(".")[-1].lower() == "clj":
            # A clojure file contains the actual "code" content
            operation["code"] = data.rstrip()
        else:
            # A JSON file contains a JSON FlureeQL query that is converted to clojure code.
            obj = json.loads(data)
            operation["code"] = query_to_clojure(obj, params)
        # Remove the code_expand key/value
        del operation["code_expand"]
    operation2 = None
    if "code_from_query" in operation:
        if not "block" in operation["code_from_query"] and "name" in operation and subdir != ".":
            operation2 = copy.deepcopy(operation)
            operation2["name"] = operation["name"] + "_previous_block"
            if "_id" in operation2 and isinstance(operation2["_id"], str) and "$" in operation2["_id"]:
                operation2["_id"] = operation2["_id"] + "_previous_block"
            operation2["code"] = query_to_clojure_previous(operation2["code_from_query"], params)
            del operation2["code_from_query"]
        # Inlined FlureeQL JSON gets converted to clojure code.
        operation["code"] = query_to_clojure(operation["code_from_query"], params)
        # Remove the code_from_query key/value
        del operation["code_from_query"]
    return operation, operation2

def expand_transaction(transaction, subdir, fluree_parts, verboseerrors):
    """Expand any "code_expand" or "code+from_query" in a transaction

    Parameters
    ----------
    transaction: list
        FlureeQL transaction list
    subdir: str
        Component directory name
    fluree_parts: str
        Fluree build sources top dir directory path
    verboseerrors: boolean
        Add extra error messages to rules that don't define them.

    Returns
    -------
    str
        Potentially expanded version of the supplied transaction
    """
    rval = list()
    for operation in transaction:
        op1, op2 = expand_operation(operation, subdir, fluree_parts, verboseerrors)
        rval.append(op1)
        if isinstance(op2,dict):
            rval.append(op2)
    return rval
