def strip_comments_obj(operation):
    """ Strip all "COMMENT" key key/value pairs from a dict.

    Parameters
    ----------
    operation: dict
        A FlureeQL operation or query

    Returns
    -------
    dict
        A copy of the supplied dict without any COMMENT key key/value data.
    """
    rval = dict()
    for key in operation.keys():
        if key != "COMMENT":
            rval[key] = operation[key]
    return rval

def strip_comments_list(transaction):
    """ Strip all "COMMENT" key key/balue pairs from a list of dicts

    Parameters
    ----------
    transaction: list
        A FlureeQL transaction.

    Returns
    -------
    str
        A copy of the supplied transaction without any COMMENT key/value data in any of the
        operations.
    """
    rval = list()
    for operation in transaction:
        rval.append(strip_comments_obj(operation))
    return rval
