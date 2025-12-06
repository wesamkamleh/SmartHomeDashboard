from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import requests
import json
from pathlib import Path
OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=52.0908"
    "&longitude=5.1222"
    "&hourly=temperature_2m,relative_humidity_2m"
    "&timezone=auto"
)

class SmartHomeApp:
    def __init__(self, root):
        root.title("Smart Home Dashboard")
        root.geometry("900x600")

        # Layout frames
        self.menu_frame = tk.Frame(root, width=200, bg="#1e90ff")
        self.menu_frame.pack(side="left", fill="y")

        self.dashboard_frame = tk.Frame(root, bg="white")
        self.dashboard_frame.pack(side="right", fill="both", expand=True)

        # Menu knoppen
        ttk.Button(self.menu_frame, text="Weer Data Laden", command=self.load_weather).pack(pady=10)
        ttk.Button(self.menu_frame, text="Grafiek Weer", command=self.show_graph).pack(pady=10)
        ttk.Button(self.menu_frame, text="SmartHome Data", command=self.show_smart_data).pack(pady=10)

        self.label = tk.Label(self.dashboard_frame, text="Dashboard Loaded", font=("Arial", 16))
        self.label.pack(pady=20)

    def load_weather(self):
        """Download weerdata van Open-Meteo en sla op in data/weather.json"""
        self.label.config(text="Weer data wordt geladen...")

        try:
            # 1. Request naar de API sturen
            response = requests.get(OPEN_METEO_URL, timeout=10)
            response.raise_for_status()  # fout als statuscode != 200

            # 2. JSON uit de response halen
            weather_data = response.json()

            # 3. data-map en bestandsnaam
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)  # maakt map als hij nog niet bestaat
            json_path = data_dir / "weather.json"

            # 4. JSON opslaan in bestand
            with json_path.open("w", encoding="utf-8") as f:
                json.dump(weather_data, f, indent=4)

            # 5. Feedback naar de gebruiker
            self.label.config(text=f"Weerdata opgeslagen in {json_path}")

        except requests.exceptions.RequestException as e:
            # Als internet / API fout gaat
            self.label.config(text=f"Fout bij ophalen weerdata: {e}")
        except Exception as e:
            # Andere fouten (bijv. wegschrijven bestand)
            self.label.config(text=f"Onverwachte fout: {e}")

    def show_graph(self):
        try:
            # JSON data laden
            with open("data/weather.json", encoding="utf-8") as f:
                data = json.load(f)

            times = data["hourly"]["time"][:24]
            temps = data["hourly"]["temperature_2m"][:24]


            for widget in self.dashboard_frame.winfo_children():
                if widget != self.label:
                    widget.destroy()


            figure = plt.Figure(figsize=(7, 4), dpi=100)
            ax = figure.add_subplot(111)
            ax.plot(times, temps, marker="o")

            # X-as labels verbeteren
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)
            for i, label in enumerate(ax.get_xticklabels()):
                if i % 3 != 0:
                    label.set_visible(False)

            ax.set_title("Temperatuur (eerste 24 uur)", fontsize=12, fontweight="bold")
            ax.set_ylabel("°C")

            figure.tight_layout()

            # In GUI plaatsen
            canvas = FigureCanvasTkAgg(figure, master=self.dashboard_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

            self.label.config(text="Grafiek geladen!")

        except FileNotFoundError:
            self.label.config(text="⚠️ Geen weerdata gevonden (klik eerst op Weer Data Laden)")
        except json.JSONDecodeError:
            self.label.config(text="⚠️ weather.json is kapot, download opnieuw")
        except Exception as e:
            self.label.config(text=f"⚠️ Fout: {e}")

    def show_smart_data(self):
        self.label.config(text="SmartHome data...")

root = tk.Tk()
app = SmartHomeApp(root)
root.mainloop()
