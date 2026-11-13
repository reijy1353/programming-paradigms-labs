# Bilet nr. 8
# Paradigma funcțională

# Sarcina 1
# Diagonala matricei: Dată fiind o matrice pătratică de numere (listă de liste), calculați suma elementelor de pe diagonala principală
def matrix_diagonal_sum(matrix):
    return sum(map(lambda i: matrix[i][i], range(len(matrix))))


# Sarcina 2
# Listă aplatizată: Dată fiind o listă ce conține liste imbricate, transformați-o într-o singură listă unidimensională
def unpack_list(l):
    return sum(map(lambda x: unpack_list(x) if isinstance(x, list) else [x], l), [])


if __name__ == "__main__":
    # Sarcina 1
    matrix = [
        [1, 2, 3, 4, 5],
        [2, 1, 3, 4, 5],
        [2, 3, 1, 4, 5],
        [2, 3, 4, 1, 5],
        [2, 3, 4, 5, 1],
    ]

    print("Results...\nSarcina 1: ", end="")
    print(matrix_diagonal_sum(matrix))
    # Result: 5

    # Sarcina 2
    # nested_list = matrix
    print("Sarcina 2: ", end="")
    print(list(unpack_list(matrix)))
    # Result: [1, 2, 3, 4, 5, 2, 1, 3, 4, 5, 2, 3, 1, 4, 5, 2, 3, 4, 1, 5, 2, 3, 4, 5, 1]
