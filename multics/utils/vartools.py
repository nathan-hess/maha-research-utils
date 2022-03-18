##############################################################################
# --- LIST UTILITIES ------------------------------------------------------- #
##############################################################################
def max_list_item_len(input_list: list):
    """Finds the maximum length of any item in a list"""
    max_len = 0

    for item in input_list:
        if (len(item) > max_len):
            max_len = len(item)

    return max_len

def list_search(name: str, search_list: list, case_sensitive: bool = False):
    """Provides a list of all list elements that match a given search term"""
    if case_sensitive:
        matches = [item for item in search_list if name in item]
    else:
        matches = [item for item in search_list if name.lower() in item.lower()]

    return matches

def check_list_types(input_list: list, compare_with_type = None, postprocess = None):
    """Analyzes type(s) of objects within a list"""
    if compare_with_type is None:
        f = lambda x: type(x)
    else:
        f = lambda x: isinstance(x, compare_with_type)
    
    type_list = list(map(f, input_list))

    if postprocess is None:
        return type_list
    else:
        return postprocess(type_list)

def check_numeric_list_equal(list1: list, list2: list, tol: float = 1e-16,
                             throw_error: bool = False):
    """Checks equality of two numeric lists element-wise"""
    # Check that lists have the same length
    if len(list1) != len(list2):
        if throw_error:
            raise ValueError('List lengths are not equal')
        else:
            return False

    # Verify that each element of the lists are equal
    for i, x in enumerate(list1):
        if (abs(x - list2[i]) > tol):
            if throw_error:
                raise ValueError(f'List elements at index {i} differ')
            else:
                return False

    return True
