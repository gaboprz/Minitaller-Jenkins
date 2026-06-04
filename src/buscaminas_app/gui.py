from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from .domain import DIFFICULTIES, MINE, generate_board, is_mine, reveal_cells, validate_settings
from .paths import asset_path, ranking_path
from .ranking import add_record, load_records, records_by_difficulty, save_records


class MinesweeperApp:
    def __init__(self, root: tk.Tk, data_file: Path | None = None) -> None:
        self.root = root
        self.data_file = data_file or ranking_path()
        self.root.title("Buscaminas")
        self.root.geometry("1000x900")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.logo = tk.PhotoImage(file=asset_path("logo.png"))
        self.original_flag = Image.open(asset_path("bandera.png"))
        self.original_mine = Image.open(asset_path("mina.png"))
        self.flag_image: ImageTk.PhotoImage | None = None
        self.mine_image: ImageTk.PhotoImage | None = None

        self.board: list[list[int]] = []
        self.buttons: dict[tuple[int, int], tk.Button] = {}
        self.flagged: set[tuple[int, int]] = set()
        self.revealed: set[tuple[int, int]] = set()
        self.remaining = tk.IntVar(value=0)
        self.elapsed_seconds = tk.IntVar(value=0)
        self.game_over = False
        self.won = False
        self.ranking_saved = False
        self.timer_job: str | None = None

    def run(self) -> None:
        self.show_menu()
        self.root.mainloop()

    def clear_root(self) -> None:
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_menu(self) -> None:
        self.clear_root()
        self.game_over = True
        self.won = False
        self.ranking_saved = False
        self.elapsed_seconds.set(0)

        tk.Label(text="Buscaminas", font="Hack 30", height=2, anchor="center").pack()
        tk.Label(image=self.logo).pack()
        for difficulty in DIFFICULTIES:
            tk.Button(
                text=difficulty.name,
                width=10,
                command=lambda config=difficulty: self.show_game(
                    config.rows, config.columns, config.mines, config.name
                ),
            ).pack()
        tk.Button(text="Personalizado", width=10, command=self.show_custom_dialog).pack()
        tk.Button(text="Ranking", width=7, command=self.show_ranking).place(x=5, y=5)

    def show_custom_dialog(self) -> None:
        custom = tk.Toplevel(self.root)
        custom.geometry("500x300")
        custom.resizable(False, False)

        rows = tk.IntVar()
        columns = tk.IntVar()
        mines = tk.IntVar()

        tk.Label(
            custom, text="Partida Personalizada", font="Hack 15", height=2, anchor="center"
        ).pack()
        tk.Label(custom, text="Filas").pack()
        tk.Entry(custom, textvariable=rows).pack()
        tk.Label(custom, text="Columnas").pack()
        tk.Entry(custom, textvariable=columns).pack()
        tk.Label(custom, text="Numero de minas").pack()
        tk.Entry(custom, textvariable=mines).pack()
        tk.Button(
            custom,
            text="Jugar",
            command=lambda: (
                custom.destroy(),
                self.show_game(rows.get(), columns.get(), mines.get(), "Personalizado"),
            ),
        ).pack(side="bottom")
        tk.Button(custom, text="Cancelar", command=custom.destroy).pack(side="bottom")

    def show_ranking(self) -> None:
        try:
            records = load_records(self.data_file)
        except json.JSONDecodeError:
            messagebox.showerror(
                "Error",
                'Los datos estan corruptos, por favor borre el archivo "data.json"',
            )
            return
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        if not records:
            messagebox.showwarning("Error", "Aun no hay victorias registradas")
            return

        grouped = records_by_difficulty(records)
        rank = tk.Toplevel(self.root)
        rank.geometry("600x600")
        rank.resizable(False, False)
        tabs = ttk.Notebook(rank)
        tabs.pack(fill="both", expand=True)

        for difficulty, difficulty_records in grouped.items():
            tab = ttk.Frame(tabs)
            tabs.add(tab, text=difficulty)
            tk.Label(tab, text=difficulty, font="Hack 20", anchor="center", height=2).pack()
            tk.Label(tab, text="Segundos").place(x=50, y=90, anchor="center")
            tk.Label(tab, text="Persona").place(x=500, y=90, anchor="center")
            times = "\n".join(str(record["tiempo"]) for record in difficulty_records)
            names = "\n".join(record["nombre"] for record in difficulty_records)
            ttk.Label(tab, text=times).place(x=50, y=120, anchor="center")
            ttk.Label(tab, text=names).place(x=500, y=120, anchor="center")

    def show_game(self, rows: int, columns: int, mines: int, difficulty: str) -> None:
        try:
            validate_settings(rows, columns, mines)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self.clear_root()
        self.board = []
        self.buttons = {}
        self.flagged = set()
        self.revealed = set()
        self.remaining.set((rows * columns) - mines)
        self.elapsed_seconds.set(0)
        self.game_over = False
        self.won = False
        self.ranking_saved = False

        button_width = 1000 // columns
        button_height = 600 // rows
        self.flag_image = ImageTk.PhotoImage(
            self.original_flag.resize((button_width // 3, button_height // 2))
        )
        self.mine_image = ImageTk.PhotoImage(
            self.original_mine.resize((button_width // 3, button_height // 2))
        )

        tk.Button(self.root, text="Salir", command=self.confirm_exit_to_menu).place(x=920, y=10)
        tk.Button(
            self.root,
            text="Reiniciar",
            command=lambda: self.confirm_restart(rows, columns, mines, difficulty),
        ).place(x=820, y=10)
        tk.Label(self.root, text="Casillas restantes:").pack()
        tk.Label(self.root, textvariable=self.remaining).pack()

        for row in range(rows):
            for column in range(columns):
                button = tk.Button(
                    bg="lightgray",
                    highlightbackground="white",
                    command=lambda r=row, c=column: self.first_click(
                        rows, columns, mines, (r, c), difficulty
                    ),
                )
                button.bind("<Button-3>", lambda _event, r=row, c=column: self.toggle_flag(r, c))
                button.place(
                    x=column * button_width,
                    y=(row * button_height) + 60,
                    height=button_height,
                    width=button_width,
                )
                self.buttons[(row, column)] = button

    def first_click(
        self,
        rows: int,
        columns: int,
        mines: int,
        cell: tuple[int, int],
        difficulty: str,
    ) -> None:
        try:
            self.board = generate_board(rows, columns, mines, cell)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        for position, button in self.buttons.items():
            if is_mine(self.board, position):
                button.config(command=lambda r=position[0], c=position[1]: self.explode(r, c))
            else:
                button.config(
                    command=lambda r=position[0], c=position[1]: self.reveal(r, c, difficulty)
                )

        tk.Label(self.root, text="Segundos transcurridos: ").place(x=80, y=20)
        tk.Label(self.root, textvariable=self.elapsed_seconds).place(x=250, y=20)
        self.start_timer()
        self.reveal(cell[0], cell[1], difficulty)

    def start_timer(self) -> None:
        if self.game_over or self.won:
            return
        self.elapsed_seconds.set(self.elapsed_seconds.get() + 1)
        self.timer_job = self.root.after(1000, self.start_timer)

    def toggle_flag(self, row: int, column: int) -> None:
        cell = (row, column)
        if cell in self.revealed:
            return
        button = self.buttons[cell]
        if cell in self.flagged:
            self.flagged.remove(cell)
            button.config(image="")
        else:
            self.flagged.add(cell)
            button.config(image=self.flag_image)

    def reveal(self, row: int, column: int, difficulty: str) -> None:
        cell = (row, column)
        revealed_now = reveal_cells(self.board, cell, self.flagged, self.revealed)
        for revealed_cell in revealed_now:
            self.revealed.add(revealed_cell)
            self.flagged.discard(revealed_cell)
            value = self.board[revealed_cell[0]][revealed_cell[1]]
            button = self.buttons[revealed_cell]
            button.config(image="", bg="darkgray", highlightbackground="darkgray")
            if value > 0:
                button.config(text=value)
        self.remaining.set(self.remaining.get() - len(revealed_now))

        if self.remaining.get() == 0 and not self.won:
            self.show_victory(difficulty)

    def show_victory(self, difficulty: str) -> None:
        self.won = True
        self.game_over = True
        name = tk.StringVar()

        victory = tk.Toplevel(self.root)
        victory.geometry("500x300")
        victory.resizable(False, False)
        victory.grab_set()
        tk.Label(victory, text="Victoria!", font="Hack 15", height=2, anchor="center").pack()
        tk.Label(victory, text="Tiempo transcurrido").pack()
        tk.Label(victory, text=f"{self.elapsed_seconds.get()} segundos").pack()
        tk.Label(victory, text="Nombre a registrar: ").pack()
        tk.Entry(victory, textvariable=name).pack()
        tk.Button(
            victory,
            text="Guardar",
            command=lambda: self.save_ranking(name.get(), difficulty),
        ).pack()
        tk.Button(victory, text="Volver al menu", command=self.show_menu).pack()
        victory.protocol("WM_DELETE_WINDOW", self.show_menu)

    def save_ranking(self, name: str, difficulty: str) -> None:
        if self.ranking_saved:
            messagebox.showwarning("Error", "Solo se puede registrar 1 vez cada victoria")
            return
        try:
            records = load_records(self.data_file)
            result = add_record(records, name, self.elapsed_seconds.get(), difficulty)
            if result.saved:
                save_records(self.data_file, result.records)
                self.ranking_saved = True
                messagebox.showinfo("Ranking", "Datos guardados correctamente!")
            else:
                messagebox.showinfo("Aviso", result.message)
        except json.JSONDecodeError:
            messagebox.showerror(
                "Error",
                'Los datos estan corruptos, por favor borre el archivo "data.json"',
            )

    def explode(self, row: int, column: int) -> None:
        if (row, column) in self.flagged:
            return
        for position, button in self.buttons.items():
            if self.board[position[0]][position[1]] == MINE:
                button.config(image=self.mine_image)

        self.game_over = True
        defeat = tk.Toplevel(self.root)
        defeat.geometry("500x300")
        defeat.resizable(False, False)
        defeat.grab_set()
        tk.Label(defeat, text="Has perdido", font="Hack 15", height=2, anchor="center").pack()
        tk.Label(defeat, text="Tiempo transcurrido").pack()
        tk.Label(defeat, text=f"{self.elapsed_seconds.get()} segundos").pack()
        tk.Button(defeat, text="Volver al menu", command=self.show_menu).pack()
        defeat.protocol("WM_DELETE_WINDOW", self.show_menu)

    def confirm_exit_to_menu(self) -> None:
        if messagebox.askyesno("Salir", "¿Esta seguro que desea salir?"):
            self.show_menu()

    def confirm_restart(self, rows: int, columns: int, mines: int, difficulty: str) -> None:
        if messagebox.askyesno(
            "Reiniciar", "¿Esta seguro que desea reiniciar? El tablero sera diferente"
        ):
            self.show_game(rows, columns, mines, difficulty)

    def exit_app(self) -> None:
        if messagebox.askyesno("Aviso", "Seguro que quieres salir?"):
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    MinesweeperApp(root).run()
