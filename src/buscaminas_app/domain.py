from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable


MINE = -1


@dataclass(frozen=True)
class Difficulty:
    name: str
    rows: int
    columns: int
    mines: int


DIFFICULTIES = (
    Difficulty("Facil", 8, 8, 10),
    Difficulty("Medio", 10, 10, 15),
    Difficulty("Dificil", 12, 12, 25),
    Difficulty("Experto", 15, 15, 40),
)


def neighbors(rows: int, columns: int, cell: tuple[int, int]) -> list[tuple[int, int]]:
    row, column = cell
    result = []
    for row_delta in (-1, 0, 1):
        for column_delta in (-1, 0, 1):
            if (row_delta, column_delta) == (0, 0):
                continue
            next_row = row + row_delta
            next_column = column + column_delta
            if 0 <= next_row < rows and 0 <= next_column < columns:
                result.append((next_row, next_column))
    return result


def validate_settings(rows: int, columns: int, mines: int) -> None:
    if rows <= 0 or columns <= 0 or mines <= 0:
        raise ValueError("No se han ingresado valores validos")
    if rows * columns < 25:
        raise ValueError("Las dimensiones minimas del tablero son de 5x5")
    if rows * columns > 400:
        raise ValueError("Las dimensiones maximas del tablero son de 20x20")
    if rows * columns - 9 < mines:
        raise ValueError("Las minas no caben en el tablero")


def protected_cells(rows: int, columns: int, first_click: tuple[int, int]) -> set[tuple[int, int]]:
    center = (rows // 2, columns // 2)
    protected = set()
    for row in range(rows):
        for column in range(columns):
            near_center = (row - center[0]) ** 2 + (column - center[1]) ** 2 <= 2
            near_first_click = (
                (row - first_click[0]) ** 2 + (column - first_click[1]) ** 2 <= 2
            )
            if near_center or near_first_click:
                protected.add((row, column))
    return protected


def mine_weight(rows: int, columns: int, cell: tuple[int, int]) -> int:
    center = (rows // 2, columns // 2)
    return (cell[0] - center[0]) ** 2 + (cell[1] - center[1]) ** 2


def generate_board(
    rows: int,
    columns: int,
    mines: int,
    first_click: tuple[int, int],
    rng: random.Random | None = None,
) -> list[list[int]]:
    validate_settings(rows, columns, mines)
    if not (0 <= first_click[0] < rows and 0 <= first_click[1] < columns):
        raise ValueError("El primer click esta fuera del tablero")

    rng = rng or random.Random()
    protected = protected_cells(rows, columns, first_click)
    candidates = [
        (row, column)
        for row in range(rows)
        for column in range(columns)
        if (row, column) not in protected
    ]
    if mines > len(candidates):
        raise ValueError("Las minas no caben respetando la zona segura")

    board = [[0 for _ in range(columns)] for _ in range(rows)]
    remaining_candidates = candidates[:]
    for _ in range(mines):
        weights = [mine_weight(rows, columns, cell) for cell in remaining_candidates]
        selected = rng.choices(remaining_candidates, weights=weights, k=1)[0]
        remaining_candidates.remove(selected)
        board[selected[0]][selected[1]] = MINE

    for row in range(rows):
        for column in range(columns):
            if board[row][column] == MINE:
                continue
            board[row][column] = sum(
                1
                for next_row, next_column in neighbors(rows, columns, (row, column))
                if board[next_row][next_column] == MINE
            )
    return board


def is_mine(board: list[list[int]], cell: tuple[int, int]) -> bool:
    return board[cell[0]][cell[1]] == MINE


def reveal_cells(
    board: list[list[int]],
    cell: tuple[int, int],
    flagged: Iterable[tuple[int, int]] | None = None,
    already_revealed: Iterable[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    flagged_set = set(flagged or [])
    revealed_set = set(already_revealed or [])
    if cell in flagged_set or cell in revealed_set or is_mine(board, cell):
        return set()

    rows = len(board)
    columns = len(board[0])
    to_reveal = {cell}
    if board[cell[0]][cell[1]] != 0:
        return to_reveal

    pending = [cell]
    visited = {cell}
    while pending:
        current = pending.pop()
        for neighbor in neighbors(rows, columns, current):
            if neighbor in visited or neighbor in flagged_set:
                continue
            if is_mine(board, neighbor):
                continue
            visited.add(neighbor)
            to_reveal.add(neighbor)
            if board[neighbor[0]][neighbor[1]] == 0:
                pending.append(neighbor)

    return to_reveal
