import tempfile
import unittest
from pathlib import Path

from buscaminas_app.ranking import add_record, load_records, save_records


class RankingTests(unittest.TestCase):
    def test_add_record_keeps_best_ten_per_difficulty(self):
        records = [
            {"nombre": f"jugador-{time}", "tiempo": time, "dificultad": "Facil"}
            for time in range(1, 11)
        ]

        result = add_record(records, "nuevo", 99, "Facil")

        self.assertFalse(result.saved)
        self.assertEqual(len(result.records), 10)

    def test_add_record_accepts_better_time(self):
        records = [
            {"nombre": f"jugador-{time}", "tiempo": time, "dificultad": "Facil"}
            for time in range(10, 20)
        ]

        result = add_record(records, "nuevo", 1, "Facil")

        self.assertTrue(result.saved)
        self.assertEqual(result.records[0]["nombre"], "nuevo")
        self.assertEqual(len(result.records), 10)

    def test_custom_difficulty_is_not_saved(self):
        result = add_record([], "Ana", 15, "Personalizado")

        self.assertFalse(result.saved)
        self.assertEqual(result.records, [])

    def test_records_can_be_persisted(self):
        records = [{"nombre": "Ana", "tiempo": 12, "dificultad": "Medio"}]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data.json"

            save_records(path, records)

            self.assertEqual(load_records(path), records)


if __name__ == "__main__":
    unittest.main()
