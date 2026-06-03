from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


RANKED_DIFFICULTIES = ("Facil", "Medio", "Dificil", "Experto")


@dataclass(frozen=True)
class RankingResult:
    records: list[dict]
    saved: bool
    message: str


def load_records(path: Path) -> list[dict]:
    try:
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except FileNotFoundError:
        return []
    if records == []:
        return []
    if not isinstance(records, list):
        raise ValueError("El ranking debe ser una lista")
    return records


def save_records(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def records_by_difficulty(records: list[dict]) -> dict[str, list[dict]]:
    grouped = {difficulty: [] for difficulty in RANKED_DIFFICULTIES}
    for record in sorted(records, key=lambda item: item["tiempo"]):
        difficulty = record.get("dificultad")
        if difficulty in grouped:
            grouped[difficulty].append(record)
    return grouped


def add_record(
    records: list[dict],
    name: str,
    elapsed_seconds: int,
    difficulty: str,
    max_records: int = 10,
) -> RankingResult:
    if difficulty == "Personalizado":
        return RankingResult(records, False, "Los tableros personalizados no se guardan")
    if difficulty not in RANKED_DIFFICULTIES:
        return RankingResult(records, False, "Dificultad no valida")
    if not name.strip():
        return RankingResult(records, False, "Digite un nombre")

    candidate = {
        "nombre": name.strip(),
        "tiempo": int(elapsed_seconds),
        "dificultad": difficulty,
    }
    next_records = sorted([*records, candidate], key=lambda item: item["tiempo"])
    grouped = records_by_difficulty(next_records)

    kept_records = []
    for ranked_difficulty in RANKED_DIFFICULTIES:
        kept_records.extend(grouped[ranked_difficulty][:max_records])

    saved = candidate in kept_records
    if not saved:
        return RankingResult(records, False, "No calificas en los 10 primeros")

    return RankingResult(
        sorted(kept_records, key=lambda item: item["tiempo"]),
        True,
        "Datos guardados correctamente",
    )
