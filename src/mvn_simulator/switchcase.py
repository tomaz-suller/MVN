value = [None]


def switch(var):
    value[0] = var


def case(var):
    if isinstance(var, list):
        return value[0] in var
    return value[0] == var
