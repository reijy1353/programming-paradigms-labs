# Lab: functional programming (no loops, no changing variables, only recursion)


# First part O_O lists
def squares_list(n: int) -> list[int]:
    """List of the squares of the natural numbers from 1 to n"""
    # Base case, nothing left to square
    if n <= 0:
        return []

    # Squares up to n - 1, then the square of n at the end
    return squares_list(n - 1) + [n * n]


def factorial(n: int) -> int:
    """Factorial of n (0! = 1)"""
    # Base case
    if n <= 0:
        return 1

    # n! = n * (n - 1)!
    return n * factorial(n - 1)


def factorials_list(n: int) -> list[int]:
    """List of the factorials from 1! to n!"""
    # Base case, no factorials left
    if n <= 0:
        return []

    # Factorials up to n - 1, then n! at the end
    return factorials_list(n - 1) + [factorial(n)]


# 2nd part sequences
def f_mult(x: int, n: int) -> int:
    """F(x, n) = x * n, using only additions (x + x + ... + x, n times)"""
    # n = 0 means no x at all
    if n == 0:
        return 0

    # Negative n, same result with the opposite sign
    if n < 0:
        return -f_mult(x, -n)

    # x * n = x + x * (n - 1)
    return x + f_mult(x, n - 1)


def f_sum(n: int) -> int:
    """F(n) = 1 + 2 + ... + n"""
    # Base case, empty sum
    if n <= 0:
        return 0

    # Sum up to n = n + sum up to n - 1
    return n + f_sum(n - 1)


def f_double_sum(n: int) -> int:
    """F(n) = sum for j = 1..n of (1 + 2 + ... + j)"""
    # Base case, empty sum
    if n <= 0:
        return 0

    # The inner sum for j = n is f_sum(n), the rest is the same for n - 1
    return f_sum(n) + f_double_sum(n - 1)


# 3rd pard lists
def GetN(L: list, n: int):
    """Get the n-th element of L (counting from 1), None if there isn't one"""
    # Empty list or bad n, no element
    if not L or n < 1:
        return None

    # The first element is the answer for n = 1
    if n == 1:
        return L[0]

    # Skip the first element and look for n - 1 in the rest
    return GetN(L[1:], n - 1)


def Set(L: list) -> list:
    """Keep only the first occurrence of every atom of L"""
    # Base case, empty list
    if not L:
        return []

    # First atom, then the same for the rest without that atom (so it won't repeat)
    return [L[0]] + Set(list(filter(lambda atom: atom != L[0], L[1:])))


def OddEven(L: list) -> list:
    """Swap the neighbors on odd and even positions (1-2, 3-4, ...)"""
    # 0 or 1 elements, nothing to swap
    if len(L) < 2:
        return L

    # Swap the first two, then do the same for the rest
    return [L[1], L[0]] + OddEven(L[2:])


def FuncList(L1: list, L2: list, F) -> list:
    """Apply F to the atoms of L1 and L2 that are on the same position"""
    # Stop when one of the lists ends
    if not L1 or not L2:
        return []

    # F on the first pair, then the same for the rest
    return [F(L1[0], L2[0])] + FuncList(L1[1:], L2[1:], F)


# Local testing
if __name__ == "__main__":
    print(squares_list(5))
    print(factorials_list(5))

    print(f_mult(4, 3))
    print(f_sum(5))
    print(f_double_sum(3))

    print(GetN(["a", "b", "c"], 2))
    print(Set([1, 2, 1, 3, 2, 4]))
    print(OddEven([1, 2, 3, 4, 5]))
    print(FuncList([1, 2, 3], [10, 20, 30], lambda a, b: a + b))