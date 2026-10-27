def multiply_list(L):
    """Multiply every element of L by 4.5"""
    if not L:
        return []

    return [L[0] * 4.5] + multiply_list(L[1:])


def multiply_list_oneliner(L):
    """Multiply every element of L by 4.5 (one-liner version) :)"""
    return list(map(lambda x: x * 4.5, L))
