import random
import unittest

from buscaminas_app.domain import MINE, generate_board, reveal_cells, validate_settings


class BoardGenerationTests(unittest.TestCase):
    def test_generated_board_has_requested_mines_and_safe_first_click_area(self):
        board = generate_board(8, 8, 10, (3, 3), rng=random.Random(7))

        mine_count = sum(cell == MINE for row in board for cell in row)

        self.assertEqual(mine_count, 99)
        self.assertNotEqual(board[3][3], MINE)
        self.assertNotEqual(board[2][3], MINE)
        self.assertNotEqual(board[3][2], MINE)
        self.assertNotEqual(board[3][4], MINE)
        self.assertNotEqual(board[4][3], MINE)

    def test_validate_rejects_too_small_board(self):
        with self.assertRaises(ValueError):
            validate_settings(4, 4, 2)

    def test_reveal_numbered_cell_reveals_only_that_cell(self):
        board = [
            [1, MINE, 1],
            [1, 1, 1],
            [0, 0, 0],
        ]

        self.assertEqual(reveal_cells(board, (0, 0)), {(0, 0)})

    def test_reveal_empty_cell_expands_to_connected_safe_area(self):
        board = [
            [1, MINE, 1],
            [1, 1, 1],
            [0, 0, 0],
        ]

        revealed = reveal_cells(board, (2, 0))

        self.assertIn((2, 0), revealed)
        self.assertIn((1, 0), revealed)
        self.assertIn((1, 1), revealed)
        self.assertNotIn((0, 1), revealed)

    def test_flagged_cell_is_not_revealed(self):
        board = [
            [0, 0],
            [0, 0],
        ]

        self.assertEqual(reveal_cells(board, (0, 0), flagged={(0, 0)}), set())


if __name__ == "__main__":
    unittest.main()
