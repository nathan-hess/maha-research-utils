def max_list_item_len(input_list: list):
    max_len = 0

    for item in input_list:
        if (len(item) > max_len):
            max_len = len(item)

    return max_len

def list_search(name: str, search_list: list, case_sensitive: bool = False):
    if case_sensitive:
        matches = [item for item in search_list if name in item]
    else:
        matches = [item for item in search_list if name.lower() in item.lower()]

    return matches
