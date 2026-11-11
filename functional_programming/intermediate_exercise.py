def multiply_list(L):
    """Multiply every element of L by 4.5"""
    if not L:
        return []

    return [L[0] * 4.5] + multiply_list(L[1:])


def multiply_list_oneliner(L):
    """Multiply every element of L by 4.5 (one-liner version) :)"""
    return list(map(lambda x: x * 4.5, L))


# Usage example
if __name__ == "__main__":
    L = [1, 2, 3, 4, 5]
    print("Normal function: ")
    print(multiply_list(L))

    print("\nOneliner function: ")
    print(multiply_list_oneliner(L))
