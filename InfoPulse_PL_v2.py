import time
import random
import threading
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pyautogui
import pyperclip
import keyboard
import re
import unicodedata
import json
import os
import sys
import math
import traceback
import tkinter as tk
import customtkinter as ctk

# --- DANE BAZOWE I ŚCIEŻKI ---
WOJEWODZTWA = [
    ("dolnośląskie", "Wrocław", 51.10, 17.03), ("kujawsko-pomorskie", "Bydgoszcz", 53.12, 18.00),
    ("lubelskie", "Lublin", 51.25, 22.57), ("lubuskie", "Gorzów Wlkp.", 52.73, 15.24),
    ("łódzkie", "Łódź", 51.75, 19.47), ("małopolskie", "Kraków", 50.06, 19.94),
    ("mazowieckie", "Warszawa", 52.23, 21.01), ("opolskie", "Opole", 50.67, 17.92),
    ("podkarpackie", "Rzeszów", 50.04, 22.00), ("podlaskie", "Białystok", 53.13, 23.16),
    ("pomorskie", "Gdańsk", 54.35, 18.65), ("śląskie", "Katowice", 50.26, 19.03),
    ("świętokrzyskie", "Kielce", 50.87, 20.63), ("warmińsko-mazurskie", "Olsztyn", 53.78, 20.48),
    ("wielkopolskie", "Poznań", 52.41, 16.93), ("zachodniopomorskie", "Szczecin", 53.43, 14.55)
]

BOOKMARKLET = 'javascript:(function(){document.addEventListener("paste",function(e){e.stopPropagation()},!0);alert("Blokada wklejania zdjeta. Sprobuj Ctrl+V.");})();'

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
CONFIG_FILE = os.path.join(BASE_DIR, 'ghost_config.json')

# --- STYLE KOSMICZNE HUD ---
HUD_BG = "#030613"         
HUD_PANEL = "#0A1128"      
HUD_CYAN = "#00F0FF"       
HUD_PINK = "#FF007C"       
HUD_TEXT = "#E0E5FF"       
HUD_FONT = ("Consolas", 13, "bold")
HUD_FONT_LG = ("Consolas", 16, "bold")

# --- FUNKCJE POMOCNICZE I API ---
def wyczysc_tekst(tekst):
    if not tekst: return ""
    tekst = str(tekst).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    return " ".join(tekst.split())

def usun_polskie_znaki(tekst):
    return unicodedata.normalize('NFD', tekst).encode('ascii', 'ignore').decode('utf-8')

def inteligentne_ucinanie(tekst, limit):
    if len(tekst) <= limit: return tekst
    skrocony = tekst[:limit - 3]
    ostatnia_spacja = skrocony.rfind(' ')
    if ostatnia_spacja > 0: return skrocony[:ostatnia_spacja] + "..."
    return skrocony + "..."

def get_current_time(): return datetime.now().strftime("%H:%M:%S")

def get_free_games():
    try:
        r = requests.get("https://www.gamerpower.com/api/giveaways?platform=pc", headers={'User-Agent': 'GhostBot/9.0'}, timeout=5)
        dane = r.json()
        if dane:
            gra = random.choice(dane[:5])
            return f"Zgarnij za darmo: {gra.get('title', '')} (zamiast {gra.get('worth', 'Free')})"
        return "Gry: Brak ofert"
    except: return "Gry: Blad API"

def get_cyber_news(wyslane_cyber):
    try:
        r = requests.get("https://niebezpiecznik.pl/feed/", timeout=5)
        root = ET.fromstring(r.content)
        for item in root.findall('./channel/item'):
            tytul = wyczysc_tekst(re.sub(r'https?://\S+|\bwww\.\S+', '', item.find('title').text))
            if tytul not in wyslane_cyber:
                wyslane_cyber.append(tytul)
                if len(wyslane_cyber) > 30: wyslane_cyber.pop(0)
                return f"CyberNews: {tytul}"
        return "CyberNews: Brak nowych"
    except: return "CyberNews: Blad RSS"

def get_antyweb_news(wyslane_anty):
    try:
        r = requests.get("https://antyweb.pl/feed", timeout=5)
        root = ET.fromstring(r.content)
        for item in root.findall('./channel/item'):
            tytul = wyczysc_tekst(re.sub(r'https?://\S+|\bwww\.\S+', '', item.find('title').text))
            if tytul not in wyslane_anty:
                wyslane_anty.append(tytul)
                if len(wyslane_anty) > 30: wyslane_anty.pop(0)
                return f"Tech: {tytul}"
        return "Tech: Brak nowych"
    except: return "Tech: Blad RSS"

def get_nasa_news():
    try:
        r = requests.get("https://www.nasa.gov/rss/dyn/breaking_news.rss", timeout=5)
        root = ET.fromstring(r.content)
        items = root.findall('.//item')
        if items:
            item = random.choice(items[:5])
            return f"NASA Space: {wyczysc_tekst(item.find('title').text)}"
        return "NASA: Brak doniesien"
    except: return "NASA: Blad RSS"

def get_hackernews():
    try:
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5).json()
        item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{random.choice(top_ids[:20])}.json", timeout=5).json()
        if 'title' in item: return f"HackerNews: {item['title']} ({item.get('score', 0)} pkt)"
        return "HackerNews: Brak danych"
    except: return "HackerNews: Blad API"

def get_earthquakes():
    try:
        r = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson", timeout=5)
        eq = r.json()['features'][0]['properties']
        return f"Trzesienie: {eq['place']} (Mag {eq['mag']})"
    except: return "Sejsmograf: Blad API"

def get_iss_position():
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        lat, lon = float(r.json()['iss_position']['latitude']), float(r.json()['iss_position']['longitude'])
        return f"ISS: Sz {lat:.2f}, Dl {lon:.2f}"
    except: return "ISS: Brak danych"

def get_on_this_day():
    try:
        url = f"https://pl.wikipedia.org/api/rest_v1/feed/onthisday/events/{datetime.now().strftime('%m')}/{datetime.now().strftime('%d')}"
        wydarzenie = random.choice(requests.get(url, headers={'User-Agent': 'GhostBot/9.0'}, timeout=5).json()['events'])
        return f"Historia ({wydarzenie.get('year', '')}): {wydarzenie.get('text', '')}"
    except: return "Kalendarz: Blad API"

def get_selected_crypto(lista_krypto):
    if not lista_krypto: return ""
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=5)
        ceny = {item['symbol']: float(item['price']) for item in r.json()}
        wyniki = [f"{k}: {ceny[f'{k}USDT']:.3f}$" if ceny[f'{k}USDT'] < 10 else f"{k}: {int(ceny[f'{k}USDT'])}$" for k in lista_krypto if f"{k}USDT" in ceny]
        return "Krypto: " + ", ".join(wyniki)
    except: return "Krypto: Blad API"

def get_nbp_rates():
    try:
        r = requests.get("http://api.nbp.pl/api/exchangerates/tables/A/?format=json", timeout=5)
        waluty = {rate['code']: round(rate['mid'], 2) for rate in r.json()[0]['rates'] if rate['code'] in ['USD', 'EUR', 'GBP']}
        return f"NBP: USD {waluty.get('USD')}zl, EUR {waluty.get('EUR')}zl, GBP {waluty.get('GBP')}zl"
    except: return "NBP: Blad API"

def get_api_trivia():
    try:
        d = requests.get("https://pl.wikipedia.org/api/rest_v1/page/random/summary", headers={'User-Agent': 'GhostBot/9.0'}, timeout=5).json()
        return f"Wiedza: {d.get('title', '')} - {d.get('extract', '')}"
    except: return "Wiedza: Brak danych"

def get_real_news(wyslane_newsy):
    try:
        r = requests.get("https://news.google.com/rss?hl=pl&gl=PL&ceid=PL:pl", timeout=5)
        for item in ET.fromstring(r.content).findall('./channel/item'):
            tytul = item.find('title').text.rsplit(" - ", 1)[0]
            tytul = wyczysc_tekst(re.sub(r'https?://\S+|\bwww\.\S+|\b[A-Za-z0-9\-]+\.(pl|com|eu|net|org)\b', '', tytul, flags=re.IGNORECASE))
            if tytul not in wyslane_newsy:
                wyslane_newsy.append(tytul)
                if len(wyslane_newsy) > 50: wyslane_newsy.pop(0)
                return f"Wiadomosci: {tytul}"
        return "Wiadomosci: Brak nowych"
    except: return "Wiadomosci: Blad RSS"

def get_real_weather(v_index):
    woj, miasto, lat, lon = WOJEWODZTWA[v_index % len(WOJEWODZTWA)]
    try:
        d = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout=5).json()['current_weather']
        return f"[{woj.upper()} - {miasto}]: {d['temperature']}C, {d['windspeed']}km/h"
    except: return f"[{woj.upper()}]: Blad pogody"

def get_air_quality(v_index):
    woj, miasto, lat, lon = WOJEWODZTWA[v_index % len(WOJEWODZTWA)]
    try:
        d = requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi,pm10", timeout=5).json()['current']
        return f"Smog [{miasto}]: AQI {d.get('european_aqi', '?')}, PM10 {d.get('pm10', '?')}ug/m3"
    except: return f"Smog [{miasto}]: Brak danych"


# ============================================================
# InfoPulse PL — modern dashboard UI
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "InfoPulse PL"
APP_VERSION = "2.0"

BG = "#0B1020"
PANEL = "#121A2D"
PANEL_ALT = "#0F1728"
BORDER = "#23314E"
ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
CYAN = "#22D3EE"
GREEN = "#22C55E"
RED = "#EF4444"
YELLOW = "#F59E0B"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
INPUT = "#0B1324"

FONT = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_SECTION = ("Segoe UI", 15, "bold")
FONT_MONO = ("Consolas", 11)

class InfoPulseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1180x780")
        self.minsize(1080, 720)
        self.bot_running = False
        self.voivodeship_index = 0
        self.wyslane_newsy, self.wyslane_cyber, self.wyslane_anty = [], [], []
        self.config = self.load_config()
        self.var_btc = ctk.BooleanVar(value=self.config.get("btc", True))
        self.var_eth = ctk.BooleanVar(value=self.config.get("eth", True))
        self.var_sol = ctk.BooleanVar(value=self.config.get("sol", False))
        self.var_doge = ctk.BooleanVar(value=self.config.get("doge", False))
        self.var_nbp = ctk.BooleanVar(value=self.config.get("nbp", True))
        self.var_weather = ctk.BooleanVar(value=self.config.get("weather", True))
        self.var_air = ctk.BooleanVar(value=self.config.get("air", True))
        self.var_news = ctk.BooleanVar(value=self.config.get("news", True))
        self.var_trivia = ctk.BooleanVar(value=self.config.get("trivia", True))
        self.var_iss = ctk.BooleanVar(value=self.config.get("iss", True))
        self.var_history = ctk.BooleanVar(value=self.config.get("history", True))
        self.var_freegames = ctk.BooleanVar(value=self.config.get("freegames", True))
        self.var_cyber = ctk.BooleanVar(value=self.config.get("cyber", True))
        self.var_earthquake = ctk.BooleanVar(value=self.config.get("earthquake", True))
        self.var_antyweb = ctk.BooleanVar(value=self.config.get("antyweb", True))
        self.var_nasa = ctk.BooleanVar(value=self.config.get("nasa", True))
        self.var_hackernews = ctk.BooleanVar(value=self.config.get("hackernews", True))
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.build_header()
        self.build_sidebar()
        self.build_main()
        self.update_status(False)

    def load_config(self):
        defaults = {
            "chars": "400", "interval": "60", "method": "Wklej: Shift+Insert",
            "speed": "Naturalnie (0.05s)", "btc": True, "eth": True,
            "sol": False, "doge": False, "nbp": True, "weather": True,
            "air": True, "news": True, "trivia": True, "iss": True,
            "history": True, "freegames": True, "cyber": True,
            "earthquake": True, "antyweb": True, "nasa": True,
            "hackernews": True
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    defaults.update(json.load(f))
            except Exception:
                pass
        return defaults

    def save_config(self):
        self.config = {
            "chars": self.entry_chars.get().strip(),
            "interval": self.entry_interval.get().strip(),
            "method": self.method_menu.get(),
            "speed": self.speed_menu.get(),
            "btc": self.var_btc.get(), "eth": self.var_eth.get(),
            "sol": self.var_sol.get(), "doge": self.var_doge.get(),
            "nbp": self.var_nbp.get(), "weather": self.var_weather.get(),
            "air": self.var_air.get(), "news": self.var_news.get(),
            "trivia": self.var_trivia.get(), "iss": self.var_iss.get(),
            "history": self.var_history.get(), "freegames": self.var_freegames.get(),
            "cyber": self.var_cyber.get(), "earthquake": self.var_earthquake.get(),
            "antyweb": self.var_antyweb.get(), "nasa": self.var_nasa.get(),
            "hackernews": self.var_hackernews.get()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.write_log("Ustawienia zapisane.")
        except Exception as e:
            self.write_log(f"Błąd zapisu konfiguracji: {e}")

    def card(self, parent, **kwargs):
        return ctk.CTkFrame(parent, fg_color=PANEL, border_color=BORDER, border_width=1, corner_radius=14, **kwargs)

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG, corner_radius=0, height=86)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(18, 4))
        header.grid_columnconfigure(0, weight=1)
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text=APP_NAME, font=FONT_TITLE, text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Polski agregator informacji • newsy • pogoda • rynek • tech • kosmos", font=("Segoe UI", 11), text_color=MUTED).pack(anchor="w", pady=(2, 0))
        self.status_badge = ctk.CTkLabel(header, text="●  ZATRZYMANY", width=150, height=34, corner_radius=17, fg_color="#2A1620", text_color=RED, font=FONT_BOLD)
        self.status_badge.grid(row=0, column=1, padx=(12, 0))

    def build_sidebar(self):
        sidebar = self.card(self, width=335)
        sidebar.grid(row=1, column=0, sticky="nsw", padx=(24, 12), pady=(8, 24))
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="STEROWANIE", font=FONT_SECTION, text_color=TEXT).pack(anchor="w", padx=18, pady=(18, 12))
        self._field_label(sidebar, "Limit długości wiadomości")
        self.entry_chars = ctk.CTkEntry(sidebar, fg_color=INPUT, border_color=BORDER, text_color=TEXT, font=FONT, height=38)
        self.entry_chars.insert(0, str(self.config["chars"]))
        self.entry_chars.pack(fill="x", padx=18)
        self._field_label(sidebar, "Interwał wysyłania (sekundy)")
        self.entry_interval = ctk.CTkEntry(sidebar, fg_color=INPUT, border_color=BORDER, text_color=TEXT, font=FONT, height=38)
        self.entry_interval.insert(0, str(self.config["interval"]))
        self.entry_interval.pack(fill="x", padx=18)
        self._field_label(sidebar, "Sposób wysyłania")
        self.method_menu = ctk.CTkOptionMenu(sidebar, values=["Wklej: Shift+Insert", "Wklej: Ctrl+V", "Symulacja pisania"], fg_color=INPUT, button_color=ACCENT, button_hover_color=ACCENT_HOVER, text_color=TEXT, font=FONT, height=38)
        self.method_menu.set(self.config["method"])
        self.method_menu.pack(fill="x", padx=18)
        self._field_label(sidebar, "Tempo pisania")
        self.speed_menu = ctk.CTkOptionMenu(sidebar, values=["Szybko (0.015s)", "Naturalnie (0.05s)", "Wolno (0.1s)"], fg_color=INPUT, button_color=ACCENT, button_hover_color=ACCENT_HOVER, text_color=TEXT, font=FONT, height=38)
        self.speed_menu.set(self.config["speed"])
        self.speed_menu.pack(fill="x", padx=18)
        ctk.CTkButton(sidebar, text="Zapisz ustawienia", command=self.save_config, fg_color=PANEL_ALT, hover_color=BORDER, border_width=1, border_color=BORDER, text_color=TEXT, font=FONT_BOLD, height=40).pack(fill="x", padx=18, pady=(24, 8))
        self.btn_toggle = ctk.CTkButton(sidebar, text="URUCHOM BOT", command=self.toggle_bot, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="white", font=("Segoe UI", 15, "bold"), height=52, corner_radius=12)
        self.btn_toggle.pack(fill="x", padx=18, pady=(6, 18))
        ctk.CTkLabel(sidebar, text="Po uruchomieniu masz 5 sekund,\naby przejść do okna czatu.", justify="left", font=("Segoe UI", 10), text_color=MUTED).pack(anchor="w", padx=18, pady=(0, 15))

    def _field_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 11, "bold"), text_color=MUTED).pack(anchor="w", padx=18, pady=(10, 5))

    def build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=1, sticky="nsew", padx=(0, 24), pady=(8, 24))
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        summary = ctk.CTkFrame(main, fg_color="transparent")
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for i in range(3): summary.grid_columnconfigure(i, weight=1)
        self.card_sources = self._summary_card(summary, 0, "ŹRÓDŁA", "17", CYAN)
        self.card_interval = self._summary_card(summary, 1, "INTERWAŁ", f"{self.config['interval']} s", GREEN)
        self.card_limit = self._summary_card(summary, 2, "LIMIT", f"{self.config['chars']} znaków", YELLOW)
        body = ctk.CTkFrame(main, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        modules = self.card(body, width=350)
        modules.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        modules.grid_propagate(False)
        ctk.CTkLabel(modules, text="ŹRÓDŁA INFORMACJI", font=FONT_SECTION, text_color=TEXT).pack(anchor="w", padx=16, pady=(16, 8))
        scroll = ctk.CTkScrollableFrame(modules, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        groups = [("Rynek", [("Bitcoin (BTC)", self.var_btc), ("Ethereum (ETH)", self.var_eth), ("Solana (SOL)", self.var_sol), ("Dogecoin (DOGE)", self.var_doge), ("Kursy NBP", self.var_nbp)]), ("Polska", [("Pogoda", self.var_weather), ("Jakość powietrza", self.var_air), ("Wiadomości", self.var_news), ("Historia dnia", self.var_history), ("Ciekawostki", self.var_trivia)]), ("Technologia", [("Cyberbezpieczeństwo", self.var_cyber), ("Antyweb / Tech", self.var_antyweb), ("Hacker News", self.var_hackernews), ("Darmowe gry PC", self.var_freegames)]), ("Świat i kosmos", [("NASA", self.var_nasa), ("Pozycja ISS", self.var_iss), ("Trzęsienia ziemi", self.var_earthquake)])]
        for group_name, entries in groups:
            ctk.CTkLabel(scroll, text=group_name.upper(), font=("Segoe UI", 10, "bold"), text_color=CYAN).pack(anchor="w", padx=8, pady=(12, 4))
            for label, variable in entries:
                ctk.CTkCheckBox(scroll, text=label, variable=variable, fg_color=ACCENT, hover_color=ACCENT_HOVER, border_color=BORDER, checkmark_color="white", text_color=TEXT, font=("Segoe UI", 11), corner_radius=4).pack(anchor="w", padx=8, pady=4)
        terminal = self.card(body)
        terminal.grid(row=0, column=1, sticky="nsew")
        terminal.grid_rowconfigure(1, weight=1)
        terminal.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(terminal, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="DZIENNIK AKTYWNOŚCI", font=FONT_SECTION, text_color=TEXT).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(top, text="Wyczyść", width=85, command=self.clear_log, fg_color=PANEL_ALT, hover_color=BORDER, border_width=1, border_color=BORDER, text_color=MUTED, font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="e")
        self.log_box = ctk.CTkTextbox(terminal, wrap="word", fg_color=INPUT, text_color="#C8F7E8", font=FONT_MONO, border_width=1, border_color=BORDER, corner_radius=10)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.log_box.insert("end", f"{APP_NAME} {APP_VERSION}\nGotowy do pracy.\nWybierz źródła informacji i uruchom bota.\n\n")
        self.log_box.configure(state="disabled")

    def _summary_card(self, parent, column, title, value, accent):
        frame = self.card(parent)
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 6, 0))
        ctk.CTkLabel(frame, text=title, font=("Segoe UI", 10, "bold"), text_color=MUTED).pack(anchor="w", padx=14, pady=(12, 2))
        label = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 19, "bold"), text_color=accent)
        label.pack(anchor="w", padx=14, pady=(0, 12))
        return label

    def update_status(self, running):
        if running:
            self.status_badge.configure(text="●  AKTYWNY", fg_color="#0F2A20", text_color=GREEN)
            self.btn_toggle.configure(text="ZATRZYMAJ BOT", fg_color=RED, hover_color="#DC2626")
        else:
            self.status_badge.configure(text="●  ZATRZYMANY", fg_color="#2A1620", text_color=RED)
            self.btn_toggle.configure(text="URUCHOM BOT", fg_color=ACCENT, hover_color=ACCENT_HOVER)

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def write_log(self, text):
        self.after(0, self._write_log_gui, text)

    def _write_log_gui(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def get_typing_delay(self):
        value = self.speed_menu.get()
        if "0.015s" in value: return 0.015
        if "0.1s" in value: return 0.1
        return 0.05

    def toggle_bot(self):
        if not self.bot_running:
            try:
                chars = int(self.entry_chars.get().strip())
                self.max_chars = chars if chars >= 50 else 400
            except Exception: self.max_chars = 400
            try:
                interval = int(self.entry_interval.get().strip())
                self.interval = interval if interval >= 5 else 60
            except Exception: self.interval = 60
            self.save_config()
            self.card_interval.configure(text=f"{self.interval} s")
            self.card_limit.configure(text=f"{self.max_chars} znaków")
            self.bot_running = True
            self.update_status(True)
            for widget in (self.entry_chars, self.entry_interval, self.method_menu): widget.configure(state="disabled")
            self.write_log(f"\n[{get_current_time()}] Bot uruchomiony | interwał {self.interval}s | limit {self.max_chars} znaków")
            threading.Thread(target=self.bot_loop, daemon=True).start()
        else:
            self.bot_running = False
            self.btn_toggle.configure(text="ZATRZYMYWANIE...", state="disabled")
            self.write_log(f"[{get_current_time()}] Zatrzymywanie bota...")

    def reset_ui_after_stop(self):
        self.update_status(False)
        self.btn_toggle.configure(state="normal")
        for widget in (self.entry_chars, self.entry_interval, self.method_menu): widget.configure(state="normal")
        self.write_log(f"[{get_current_time()}] Bot zatrzymany.")

    def bot_loop(self):
        for i in range(5, 0, -1):
            if not self.bot_running: break
            self.write_log(f"Start za {i} s...")
            time.sleep(1)
        while self.bot_running:
            try:
                informacje = []
                wybrane_krypto = [k for k, v in [("BTC", self.var_btc), ("ETH", self.var_eth), ("SOL", self.var_sol), ("DOGE", self.var_doge)] if v.get()]
                if wybrane_krypto:
                    txt = get_selected_crypto(wybrane_krypto)
                    if txt: informacje.append(txt)
                if self.var_nbp.get(): informacje.append(get_nbp_rates())
                if self.var_weather.get(): informacje.append(get_real_weather(self.voivodeship_index))
                if self.var_air.get(): informacje.append(get_air_quality(self.voivodeship_index))
                if self.var_news.get(): informacje.append(get_real_news(self.wyslane_newsy))
                if self.var_trivia.get(): informacje.append(get_api_trivia())
                if self.var_iss.get(): informacje.append(get_iss_position())
                if self.var_history.get(): informacje.append(get_on_this_day())
                if self.var_freegames.get(): informacje.append(get_free_games())
                if self.var_cyber.get(): informacje.append(get_cyber_news(self.wyslane_cyber))
                if self.var_earthquake.get(): informacje.append(get_earthquakes())
                if self.var_antyweb.get(): informacje.append(get_antyweb_news(self.wyslane_anty))
                if self.var_nasa.get(): informacje.append(get_nasa_news())
                if self.var_hackernews.get(): informacje.append(get_hackernews())
                cleaned = [wyczysc_tekst(x) for x in informacje if x]
                random.shuffle(cleaned)
                msg = f"{get_current_time()} | " + " | ".join(cleaned) if cleaned else get_current_time()
                msg = inteligentne_ucinanie(msg, self.max_chars)
                method = self.method_menu.get()
                if "Symulacja" in method:
                    keyboard.write(usun_polskie_znaki(msg), delay=self.get_typing_delay())
                elif "Ctrl+V" in method:
                    pyperclip.copy(msg); pyautogui.hotkey("ctrl", "v")
                else:
                    pyperclip.copy(msg); pyautogui.hotkey("shift", "insert")
                time.sleep(0.5)
                pyautogui.press("enter")
                self.write_log(f"\n[{get_current_time()}] Wysłano ({len(msg)} znaków)\n{msg}")
                self.voivodeship_index += 1
                for _ in range(self.interval):
                    if not self.bot_running: break
                    time.sleep(1)
            except Exception as e:
                self.write_log(f"Błąd procesu: {e}")
                time.sleep(5)
        self.after(0, self.reset_ui_after_stop)

if __name__ == "__main__":
    try:
        app = InfoPulseApp()
        app.mainloop()
    except Exception:
        traceback.print_exc()
        input("\nNaciśnij ENTER, aby zamknąć program...")
