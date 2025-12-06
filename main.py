import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DATA_FILE = Path("data") / "gym_visits.json"


class SmartGymDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SmartGym – Bezoekers Dashboard")
        self.geometry("1000x600")

        # Live update ON/OFF toggle
        self.live_update_enabled = False

        # MENU FRAME
        self.menu_frame = tk.Frame(self, bg="#007bff", width=180)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # CONTENT FRAME
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.status_label = tk.Label(
            self.content_frame,
            text="Welkom bij SmartGym Dashboard",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        self.status_label.pack(pady=10)

        self.info_frame = tk.Frame(self.content_frame, bg="white")
        self.info_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # MENU BUTTONS
        ttk.Button(self.menu_frame, text="Live overzicht", command=self.show_live_overview).pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(self.menu_frame, text="Grafiek drukte", command=self.show_hourly_graph).pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(self.menu_frame, text="Live Update Mode", command=self.enable_auto_update).pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(self.menu_frame, text="Voorspelling AI", command=self.show_prediction).pack(padx=10, pady=10, fill=tk.X)
        ttk.Button(self.menu_frame, text="SDG-Uitleg", command=self.show_sdg).pack(padx=10, pady=10, fill=tk.X)

    # HELPER FUNCTIES --------------------------------------------------

    def _load_data(self):
        with DATA_FILE.open() as f:
            return json.load(f)

    def _save_data(self, data):
        with DATA_FILE.open("w") as f:
            json.dump(data, f, indent=4)

    def _clear_info(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

    # LIVE OVERZICHT -------------------------------------------------------

    def show_live_overview(self):
        try:
            data = self._load_data()

            current = data["current_visitors"]
            max_c = data["max_capacity"]
            last_in = data.get("last_entry", "-")
            last_out = data.get("last_exit", "-")

            ratio = current / max_c
            kleur = "green"
            waarschuwing = ""

            if ratio >= 0.9:
                kleur = "red"
                waarschuwing = "\n⚠️ MAX capaciteit bijna bereikt!"
            elif ratio >= 0.7:
                kleur = "orange"
                waarschuwing = "\n⚠️ Het wordt druk!"

            txt = (
                f"Huidig aantal bezoekers: {current}/{max_c}\n"
                f"Laatst binnen: {last_in}\n"
                f"Laatst vertrokken: {last_out}"
                f"{waarschuwing}"
            )

            self._clear_info()
            tk.Label(self.info_frame, text="Live overzicht", bg="white", font=("Arial", 20, "bold")).pack(pady=5)
            tk.Label(self.info_frame, text=txt, bg="white", font=("Arial", 16), fg=kleur).pack()

        except Exception as e:
            self.status_label.config(text=f"FOUT: {e}", fg="red")

    # GRAFIEK ---------------------------------------------------------

    def show_hourly_graph(self):
        try:
            data = self._load_data()
            values = data["visitors_per_hour"]
            hours = list(range(len(values)))

            self._clear_info()

            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(hours, values, color="#007bff")
            ax.set_title("Drukte per uur", fontsize=14)
            ax.set_xlabel("Uur")
            ax.set_ylabel("Bezoekers")
            ax.set_xticks(hours)
            ax.set_xticklabels(hours, rotation=45, ha="right")

            canvas = FigureCanvasTkAgg(fig, master=self.info_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

            self.status_label.config(text="Grafiek weergegeven")

        except Exception as e:
            self.status_label.config(text=f"FOUT: {e}", fg="red")

    # LIVE UPDATE MODE FIXED ---------------------------------------------------------

    def enable_auto_update(self):
        self.live_update_enabled = not self.live_update_enabled

        if not self.live_update_enabled:
            self.status_label.config(text="Live update UIT", fg="red")
            return

        self.status_label.config(text="Live update AAN", fg="green")
        self.update_live_data()

    def update_live_data(self):
        if not self.live_update_enabled:
            return

        try:
            import random
            data = self._load_data()
            change = random.choice([-1, 1])
            data["current_visitors"] = max(0, min(data["current_visitors"] + change, data["max_capacity"]))
            self._save_data(data)

            self.show_live_overview()
            self.after(10000, self.update_live_data)

        except Exception as e:
            self.status_label.config(text=f"FOUT: {e}", fg="red")

    # AI ------------------------------------------------------------

    def show_prediction(self):
        try:
            data = self._load_data()
            current = data["current_visitors"]
            max_c = data["max_capacity"]
            predicted = current + int((max_c - current) * 0.2)

            self._clear_info()
            tk.Label(self.info_frame, text=f"📈 Verwachte drukte over 1 uur: {predicted}", font=("Arial", 18, "bold"), bg="white", fg="purple").pack(pady=50)

            self.status_label.config(text="Voorspelling AI getoond")

        except Exception as e:
            self.status_label.config(text=f"FOUT: {e}", fg="red")

    # SDG ------------------------------------------------------------

    def show_sdg(self):
        self._clear_info()

        txt = (
            "🌱 SDG - Duurzame Impact\n\n"
            "SmartGym helpt minder energie gebruiken:\n\n"
            "• Minder airco bij lage bezetting\n"
            "• Slimme planning personeel\n"
            "• Lager stroomverbruik = minder CO₂\n\n"
            "SDG 9 – Industrie, innovatie & infrastructuur\n"
            "SDG 12 – Verantwoorde consumptie"
        )

        tk.Label(self.info_frame, text=txt, font=("Arial", 14), bg="white", justify="left").pack(padx=20, pady=20)
        self.status_label.config(text="SDG uitleg getoond")


if __name__ == "__main__":
    app = SmartGymDashboard()
    app.mainloop()
