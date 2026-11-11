# ruff: noqa: C417

from itertools import product

# Size of the board
N = 8

# Jumps of a knight (row change, column change)
KNIGHT_JUMPS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]


# All squares
def all_squares(n):
    """All the squares of an n x n board as (row, column), row by row"""
    return list(product(range(n), repeat=2))


# Attack patter (who attacks who)
def rook_attacks(a, b):
    """A rook attacks on the same row or on the same column"""
    return a[0] == b[0] or a[1] == b[1]


def bishop_attacks(a, b):
    """A bishop attacks on the diagonals, same distance on rows and columns"""
    return abs(a[0] - b[0]) == abs(a[1] - b[1])


def queen_attacks(a, b):
    """A queen attacks like a rook and like a bishop"""
    return rook_attacks(a, b) or bishop_attacks(a, b)


def knight_attacks(a, b):
    """A knight attacks 2 squares in one direction and 1 in the other"""
    return (abs(a[0] - b[0]), abs(a[1] - b[1])) in [(1, 2), (2, 1)]


# Search functions
def free_squares(piece, squares, attacks):
    """The squares from the list that the piece does not attack"""
    return list(filter(lambda square: not attacks(piece, square), squares))


def with_piece(piece, all_placements):
    """Add the piece at the start of every placement"""
    return list(map(lambda placement: [piece] + placement, all_placements))


def placements(squares, attacks, size):
    """All the ways to put 'size' pieces on 'squares', none attacking another"""
    # Nothing left to place, check or empty placement
    if size == 0:
        return [[]]

    # Not enough squares left for all the pieces
    if len(squares) < size:
        return []

    # The ways that use the first square + the ways that skip it
    # (a piece on the first square removes the squares it attacks)
    return with_piece(
        squares[0],
        placements(free_squares(squares[0], squares[1:], attacks), attacks, size - 1),
    ) + placements(squares[1:], attacks, size)


# Sarcina 1 - 4
# The maximum number of pieces (works for boards of 4 x 4 or bigger)
def bishop_placements(n):
    """All the placements of 2n - 2 bishops (the maximum)"""
    return placements(all_squares(n), bishop_attacks, 2 * n - 2)


def rook_placements(n):
    """All the placements of n rooks (one on every row, the maximum)"""
    return placements(all_squares(n), rook_attacks, n)


def knight_placements(n):
    """All the placements of half of the squares as knights (the maximum)"""
    return placements(all_squares(n), knight_attacks, (n * n + 1) // 2)


def queen_placements(n):
    """All the placements of n queens (one on every row, the maximum)"""
    return placements(all_squares(n), queen_attacks, n)


# Sarcina 5
def knight_moves(square, n):
    """The squares of the board where a knight on 'square' can jump"""
    return list(
        filter(
            lambda s: 0 <= s[0] < n and 0 <= s[1] < n,
            map(lambda jump: (square[0] + jump[0], square[1] + jump[1]), KNIGHT_JUMPS),
        )
    )


def free_moves(path, n):
    """The jumps from the last square of the path to squares not visited yet"""
    return list(filter(lambda s: s not in path, knight_moves(path[-1], n)))


def best_first(path, n):
    """The free jumps, the ones with the fewest exits first (Warnsdorff rule)"""
    return sorted(free_moves(path, n), key=lambda s: len(free_moves(path + [s], n)))


def try_moves(path, moves, n):
    """Try the moves one by one, the first one that ends in a full tour wins"""
    # No moves left, this path is a dead end
    if not moves:
        return None

    # 'or' takes the first result if it is a tour (a non-empty list), else tries the rest
    return knight_tour(path + [moves[0]], n) or try_moves(path, moves[1:], n)


def knight_tour(path, n):
    """Continue the path until every square is visited, None if it is impossible"""
    # Every square is visited
    if len(path) == n * n:
        return path

    return try_moves(path, best_first(path, n), n)


# Print (results)
def board_text(placement, n):
    """Draw the board, X for a piece and . for an empty square"""
    return "\n".join(
        map(
            lambda row: " ".join(
                map(lambda col: "X" if (row, col) in placement else ".", range(n))
            ),
            range(n),
        )
    )


def tour_text(path, n):
    """Draw the board with the number of the step on every square"""
    return "\n".join(
        map(
            lambda row: " ".join(
                map(lambda col: str(path.index((row, col)) + 1).rjust(2), range(n))
            ),
            range(n),
        )
    )


def show(title, results, n):
    """Print how many placements were found and draw the first one"""
    # No placement found
    if not results:
        print(title, "- none")
        return

    print(title, "-", len(results), "placements of", len(results[0]), "pieces")
    print("First one:")
    print(board_text(results[0], n))
    print()


if __name__ == "__main__":
    show("Bishops", bishop_placements(N), N)
    show("Rooks", rook_placements(N), N)
    show("Knights", knight_placements(N), N)
    show("Queens", queen_placements(N), N)

    print("Knight tour from the corner:")
    print(tour_text(knight_tour([(0, 0)], N), N))
