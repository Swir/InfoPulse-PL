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
import ctypes
from ctypes import wintypes
from pynput.keyboard import Key, Controller
import tkinter as tk
import customtkinter as ctk
from urllib.parse import quote_plus

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


if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
CONFIG_FILE = os.path.join(BASE_DIR, 'infopulse_config.json')


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
    except: return "Gry: Błąd API"

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
    except: return "CyberNews: Błąd RSS"

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
    except: return "Tech: Błąd RSS"

def get_nasa_news():
    try:
        r = requests.get("https://www.nasa.gov/rss/dyn/breaking_news.rss", timeout=5)
        root = ET.fromstring(r.content)
        items = root.findall('.//item')
        if items:
            item = random.choice(items[:5])
            return f"NASA Space: {wyczysc_tekst(item.find('title').text)}"
        return "NASA: Brak doniesień"
    except: return "NASA: Błąd RSS"

def get_hackernews():
    try:
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5).json()
        item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{random.choice(top_ids[:20])}.json", timeout=5).json()
        if 'title' in item: return f"HackerNews: {item['title']} ({item.get('score', 0)} pkt)"
        return "HackerNews: Brak danych"
    except: return "HackerNews: Błąd API"

def get_earthquakes():
    try:
        r = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson", timeout=5)
        eq = r.json()['features'][0]['properties']
        return f"Trzęsienie: {eq['place']} (Mag {eq['mag']})"
    except: return "Sejsmograf: Błąd API"

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
    except: return "Kalendarz: Błąd API"

def get_selected_crypto(lista_krypto):
    if not lista_krypto: return ""
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=5)
        ceny = {item['symbol']: float(item['price']) for item in r.json()}
        wyniki = [f"{k}: {ceny[f'{k}USDT']:.3f}$" if ceny[f'{k}USDT'] < 10 else f"{k}: {int(ceny[f'{k}USDT'])}$" for k in lista_krypto if f"{k}USDT" in ceny]
        return "Krypto: " + ", ".join(wyniki)
    except: return "Krypto: Błąd API"

def get_nbp_rates():
    try:
        r = requests.get("http://api.nbp.pl/api/exchangerates/tables/A/?format=json", timeout=5)
        waluty = {rate['code']: round(rate['mid'], 2) for rate in r.json()[0]['rates'] if rate['code'] in ['USD', 'EUR', 'GBP']}
        return f"NBP: USD {waluty.get('USD')}zl, EUR {waluty.get('EUR')}zl, GBP {waluty.get('GBP')}zl"
    except: return "NBP: Błąd API"

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
                return f"Wiadomości: {tytul}"
        return "Wiadomości: Brak nowych"
    except: return "Wiadomości: Blad RSS"

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
# InfoPulse PL v3 MAX — dodatkowe darmowe źródła
# ============================================================

USER_AGENT = "InfoPulsePL/3.0 (+https://github.com/Swir/InfoPulse-PL)"

RSS_SOURCES = {
    "rmf_main": ("RMF24", "https://www.rmf24.pl/feed", "RMF24"),
    "rmf_poland": ("RMF24 Polska", "https://www.rmf24.pl/fakty/polska/feed", "Polska"),
    "rmf_world": ("RMF24 Świat", "https://www.rmf24.pl/fakty/swiat/feed", "Świat"),
    "rmf_economy": ("RMF24 Ekonomia", "https://www.rmf24.pl/ekonomia/feed", "Ekonomia"),
    "rmf_science": ("RMF24 Nauka", "https://www.rmf24.pl/nauka/feed", "Nauka"),
    "rmf_sport": ("RMF24 Sport", "https://www.rmf24.pl/sport/feed", "Sport"),
    "rmf_weather": ("RMF24 Pogoda", "https://www.rmf24.pl/pogoda/feed", "Pogoda"),
    "rmf_curiosity": ("RMF24 Ciekawostki", "https://www.rmf24.pl/rozrywka/ciekawostki/feed", "Ciekawostki"),
    "ars": ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "Ars"),
}

SERVICE_STATUS = {
    "github_status": ("GitHub", "https://www.githubstatus.com/api/v2/status.json"),
    "cloudflare_status": ("Cloudflare", "https://www.cloudflarestatus.com/api/v2/status.json"),
    "openai_status": ("OpenAI", "https://status.openai.com/api/v2/status.json"),
}

_seen_global = {}


def _http_get(url, timeout=7):
    return requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)


def _remember(source, value, limit=80):
    if not value:
        return False
    bucket = _seen_global.setdefault(source, [])
    if value in bucket:
        return False
    bucket.append(value)
    if len(bucket) > limit:
        del bucket[:-limit]
    return True


def get_rss_item(source_key):
    if source_key not in RSS_SOURCES:
        return ""
    name, url, prefix = RSS_SOURCES[source_key]
    try:
        r = _http_get(url)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        items = root.findall("./channel/item")
        if items:
            for item in items[:15]:
                node = item.find("title")
                title = wyczysc_tekst(node.text if node is not None else "")
                if title and _remember(source_key, title):
                    return f"{prefix}: {title}"

        ns = {"a": "http://www.w3.org/2005/Atom"}
        entries = root.findall("a:entry", ns)
        for entry in entries[:15]:
            node = entry.find("a:title", ns)
            title = wyczysc_tekst(node.text if node is not None else "")
            if title and _remember(source_key, title):
                return f"{prefix}: {title}"

        return f"{name}: Brak nowych"
    except Exception:
        return f"{name}: Błąd RSS"


def get_service_status(service_key):
    if service_key not in SERVICE_STATUS:
        return ""
    name, url = SERVICE_STATUS[service_key]
    try:
        data = _http_get(url).json()
        status = data.get("status", {})
        desc = status.get("description", "Brak danych")
        indicator = status.get("indicator", "?")
        return f"Status {name}: {desc} [{indicator}]"
    except Exception:
        return f"Status {name}: Błąd API"


def get_iss_position_v3():
    try:
        d = _http_get("https://api.wheretheiss.at/v1/satellites/25544").json()
        return (
            f"ISS: {float(d.get('latitude', 0)):.2f}, {float(d.get('longitude', 0)):.2f} | "
            f"{float(d.get('altitude', 0)):.0f} km | {float(d.get('velocity', 0)):.0f} km/h"
        )
    except Exception:
        return get_iss_position()


def get_uv_index(v_index):
    woj, miasto, lat, lon = WOJEWODZTWA[v_index % len(WOJEWODZTWA)]
    try:
        url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}&current=uv_index"
        )
        d = _http_get(url).json().get("current", {})
        return f"UV [{miasto}]: indeks {d.get('uv_index', '?')}"
    except Exception:
        return f"UV [{miasto}]: Brak danych"


def get_marine_conditions():
    try:
        url = (
            "https://marine-api.open-meteo.com/v1/marine"
            "?latitude=54.35&longitude=18.65"
            "&current=wave_height,wave_direction,wave_period"
        )
        d = _http_get(url).json().get("current", {})
        return (
            f"Bałtyk/Gdańsk: fala {d.get('wave_height', '?')} m, "
            f"kier. {d.get('wave_direction', '?')}°, okres {d.get('wave_period', '?')} s"
        )
    except Exception:
        return "Bałtyk: Brak danych"


def get_github_trending_events():
    try:
        events = _http_get("https://api.github.com/events?per_page=20").json()
        for e in events:
            repo = (e.get("repo") or {}).get("name")
            etype = e.get("type", "")
            if repo and _remember("github_events", f"{etype}:{repo}"):
                return f"GitHub Live: {etype} → {repo}"
        return "GitHub Live: Brak nowych"
    except Exception:
        return "GitHub Live: Błąd API"


def get_random_joke():
    try:
        d = _http_get("https://official-joke-api.appspot.com/random_joke").json()
        setup = wyczysc_tekst(d.get("setup", ""))
        punch = wyczysc_tekst(d.get("punchline", ""))
        if setup and punch:
            return f"Humor: {setup} — {punch}"
        return "Humor: Brak danych"
    except Exception:
        return "Humor: Błąd API"



# ============================================================
# Bezpośrednie wpisywanie Unicode w Windows (bez schowka)
# ============================================================

def type_unicode_windows(text, delay=0.01):
    """
    Wpisuje tekst znak po znaku przez Windows SendInput.
    Nie używa Ctrl+V, Shift+Insert ani schowka.
    Obsługuje również polskie znaki Unicode.
    """
    if os.name != "nt":
        # Fallback na innych systemach
        keyboard.write(usun_polskie_znaki(text), delay=delay)
        return

    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004

    ULONG_PTR = wintypes.WPARAM

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [
            ("type", wintypes.DWORD),
            ("u", INPUT_UNION),
        ]

    send_input = ctypes.windll.user32.SendInput

    for ch in text:
        # UTF-16: obsługa zwykłych znaków i par surogatów
        encoded = ch.encode("utf-16-le")
        units = [int.from_bytes(encoded[i:i+2], "little") for i in range(0, len(encoded), 2)]

        for unit in units:
            key_down = INPUT(
                type=INPUT_KEYBOARD,
                ki=KEYBDINPUT(
                    wVk=0,
                    wScan=unit,
                    dwFlags=KEYEVENTF_UNICODE,
                    time=0,
                    dwExtraInfo=0,
                ),
            )
            key_up = INPUT(
                type=INPUT_KEYBOARD,
                ki=KEYBDINPUT(
                    wVk=0,
                    wScan=unit,
                    dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=0,
                ),
            )

            send_input(1, ctypes.byref(key_down), ctypes.sizeof(INPUT))
            send_input(1, ctypes.byref(key_up), ctypes.sizeof(INPUT))

        if delay:
            time.sleep(delay)



# ============================================================
# WŁASNE ŹRÓDŁA UŻYTKOWNIKA — RSS / ATOM / JSON API
# ============================================================

def _json_path_get(data, path):
    """Pobiera wartość ze struktury JSON po ścieżce np. data.items.0.title."""
    if not path:
        return data

    current = data
    for part in path.split("."):
        part = part.strip()
        if not part:
            continue

        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None

        elif isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]

        else:
            return None

    return current


def _extract_useful_json_text(value):
    """Zamienia typową odpowiedź JSON na krótki tekst do wysłania."""
    if value is None:
        return ""

    if isinstance(value, (str, int, float, bool)):
        return str(value)

    if isinstance(value, list):
        if not value:
            return ""
        return _extract_useful_json_text(value[0])

    if isinstance(value, dict):
        for key in ("title", "name", "message", "description", "text", "value", "status"):
            if key in value:
                return _extract_useful_json_text(value[key])

        # Fallback: pierwszy prosty element
        for value_item in value.values():
            text = _extract_useful_json_text(value_item)
            if text:
                return text

    return ""


def get_custom_source(source):
    """
    Obsługuje własne źródła:
    - RSS / Atom
    - JSON API GET
    """
    name = wyczysc_tekst(source.get("name", "Własne źródło"))
    source_type = source.get("type", "RSS").upper()
    url = source.get("url", "").strip()
    prefix = wyczysc_tekst(source.get("prefix", name))
    timeout = 8

    if not url:
        return f"{prefix}: Brak adresu URL"

    try:
        headers = {"User-Agent": USER_AGENT}
        custom_headers = source.get("headers", {})

        if isinstance(custom_headers, str):
            try:
                custom_headers = json.loads(custom_headers) if custom_headers.strip() else {}
            except Exception:
                custom_headers = {}

        if isinstance(custom_headers, dict):
            headers.update({str(k): str(v) for k, v in custom_headers.items()})

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        if source_type in ("RSS", "ATOM"):
            root = ET.fromstring(response.content)

            items = root.findall("./channel/item")
            if items:
                for item in items[:20]:
                    title_node = item.find("title")
                    title = wyczysc_tekst(title_node.text if title_node is not None else "")
                    if title and _remember(f"custom:{url}", title):
                        return f"{prefix}: {title}"

            ns = {"a": "http://www.w3.org/2005/Atom"}
            entries = root.findall("a:entry", ns)
            for entry in entries[:20]:
                title_node = entry.find("a:title", ns)
                title = wyczysc_tekst(title_node.text if title_node is not None else "")
                if title and _remember(f"custom:{url}", title):
                    return f"{prefix}: {title}"

            return f"{prefix}: Brak nowych wpisów"

        data = response.json()
        value = _json_path_get(data, source.get("json_path", "").strip())
        text = wyczysc_tekst(_extract_useful_json_text(value))

        if not text:
            return f"{prefix}: Brak danych pod wskazaną ścieżką"

        return f"{prefix}: {text}"

    except Exception as exc:
        return f"{prefix}: Błąd źródła ({type(exc).__name__})"


# ============================================================
# InfoPulse PL — modern dashboard UI
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "InfoPulse PL"
APP_VERSION = "3.2 MAX"

pynput_keyboard = Controller()

BG = "#050816"
PANEL = "#0C1224"
PANEL_ALT = "#09101E"
BORDER = "#1E2B45"
ACCENT = "#00E5FF"
ACCENT_HOVER = "#00B8D4"
CYAN = "#00F5FF"
GREEN = "#39FF88"
RED = "#FF477E"
YELLOW = "#FFD166"
TEXT = "#F5F7FF"
MUTED = "#8390AA"
INPUT = "#060B16"
PURPLE = "#9B5CFF"
MAGENTA = "#FF4FD8"
CARD_BG = "#08101F"

FONT = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_SECTION = ("Segoe UI", 15, "bold")
FONT_MONO = ("Consolas", 11)

class InfoPulseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1320x880")
        self.minsize(1100, 720)
        self.bot_running = False
        self.voivodeship_index = 0
        self.wyslane_newsy, self.wyslane_cyber, self.wyslane_anty = [], [], []
        self.config = self.load_config()
        self.custom_sources = self.config.get("custom_sources", [])
        self.custom_source_vars = [
            ctk.BooleanVar(value=source.get("enabled", True))
            for source in self.custom_sources
        ]
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
        self.var_uv = ctk.BooleanVar(value=self.config.get("uv", True))
        self.var_marine = ctk.BooleanVar(value=self.config.get("marine", False))
        self.var_rmf_main = ctk.BooleanVar(value=self.config.get("rmf_main", True))
        self.var_rmf_world = ctk.BooleanVar(value=self.config.get("rmf_world", True))
        self.var_rmf_economy = ctk.BooleanVar(value=self.config.get("rmf_economy", True))
        self.var_rmf_science = ctk.BooleanVar(value=self.config.get("rmf_science", False))
        self.var_rmf_sport = ctk.BooleanVar(value=self.config.get("rmf_sport", False))
        self.var_ars = ctk.BooleanVar(value=self.config.get("ars", True))
        self.var_github_status = ctk.BooleanVar(value=self.config.get("github_status", True))
        self.var_cloudflare_status = ctk.BooleanVar(value=self.config.get("cloudflare_status", False))
        self.var_openai_status = ctk.BooleanVar(value=self.config.get("openai_status", True))
        self.var_github_events = ctk.BooleanVar(value=self.config.get("github_events", False))
        self.var_joke = ctk.BooleanVar(value=self.config.get("joke", False))
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
            "chars": "400", "interval": "60", "method": "Pynput Mode (najlepszy)",
            "speed": "Naturalnie (0.05s)",
            "btc": True, "eth": True, "sol": False, "doge": False,
            "nbp": True, "weather": True, "air": True, "news": True,
            "trivia": True, "iss": True, "history": True, "freegames": True,
            "cyber": True, "earthquake": True, "antyweb": True,
            "nasa": True, "hackernews": True,
            "uv": True, "marine": False,
            "rmf_main": True, "rmf_world": True, "rmf_economy": True,
            "rmf_science": False, "rmf_sport": False,
            "ars": True,
            "github_status": True, "cloudflare_status": False,
            "openai_status": True,
            "github_events": False, "joke": False,
            "custom_sources": []
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    defaults.update(json.load(f))
            except Exception:
                pass
        return defaults

    def sync_custom_source_states(self):
        """Synchronizuje przełączniki własnych źródeł z konfiguracją."""
        for index, var in enumerate(self.custom_source_vars):
            if index < len(self.custom_sources):
                self.custom_sources[index]["enabled"] = bool(var.get())

    def save_config(self):
        self.config = {
            "chars": self.entry_chars.get().strip(),
            "interval": self.entry_interval.get().strip(),
            "method": self.method_menu.get(),
            "speed": self.speed_menu.get(),
            "btc": self.var_btc.get(),
            "eth": self.var_eth.get(),
            "sol": self.var_sol.get(),
            "doge": self.var_doge.get(),
            "nbp": self.var_nbp.get(),
            "weather": self.var_weather.get(),
            "air": self.var_air.get(),
            "news": self.var_news.get(),
            "trivia": self.var_trivia.get(),
            "iss": self.var_iss.get(),
            "history": self.var_history.get(),
            "freegames": self.var_freegames.get(),
            "cyber": self.var_cyber.get(),
            "earthquake": self.var_earthquake.get(),
            "antyweb": self.var_antyweb.get(),
            "nasa": self.var_nasa.get(),
            "hackernews": self.var_hackernews.get(),
            "uv": self.var_uv.get(),
            "marine": self.var_marine.get(),
            "rmf_main": self.var_rmf_main.get(),
            "rmf_world": self.var_rmf_world.get(),
            "rmf_economy": self.var_rmf_economy.get(),
            "rmf_science": self.var_rmf_science.get(),
            "rmf_sport": self.var_rmf_sport.get(),
            "ars": self.var_ars.get(),
            "github_status": self.var_github_status.get(),
            "cloudflare_status": self.var_cloudflare_status.get(),
            "openai_status": self.var_openai_status.get(),
            "github_events": self.var_github_events.get(),
            "joke": self.var_joke.get(),
            "custom_sources": self.custom_sources,
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
        header = ctk.CTkFrame(self, fg_color="#070B16", corner_radius=0, height=96)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        logo = ctk.CTkFrame(
            header, width=58, height=58, corner_radius=16,
            fg_color="#0A1630", border_width=1, border_color=CYAN
        )
        logo.grid(row=0, column=0, padx=(22, 14), pady=18)
        logo.grid_propagate(False)

        ctk.CTkLabel(
            logo, text="IP",
            font=("Segoe UI", 20, "bold"),
            text_color=CYAN
        ).place(relx=0.5, rely=0.5, anchor="center")

        box = ctk.CTkFrame(header, fg_color="transparent")
        box.grid(row=0, column=1, sticky="w", pady=16)

        ctk.CTkLabel(
            box,
            text="INFOPULSE // CENTRUM DOWODZENIA",
            font=("Segoe UI", 26, "bold"),
            text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            box,
            text="DANE NA ŻYWO • AUTOCHAT • AGREGATOR INFORMACJI",
            font=("Consolas", 10, "bold"),
            text_color=CYAN
        ).pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=2, padx=22, pady=16, sticky="e")

        self.status_badge = ctk.CTkLabel(
            right,
            text="●  BOT WYŁĄCZONY",
            font=("Segoe UI", 12, "bold"),
            text_color=RED,
            fg_color="#170B16",
            corner_radius=12,
            padx=16,
            pady=8
        )
        self.status_badge.pack(anchor="e")

        ctk.CTkLabel(
            right,
            text="v3.2 MAX • SILNIK PYNPUT",
            font=("Consolas", 9, "bold"),
            text_color=MUTED
        ).pack(anchor="e", pady=(7, 0))

    def build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=300, fg_color="#080D19", corner_radius=0)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="PANEL STEROWANIA",
            font=("Consolas", 12, "bold"),
            text_color=CYAN
        ).pack(anchor="w", padx=20, pady=(20, 14))

        self._field_label(sidebar, "Limit znaków wiadomości")
        self.entry_chars = ctk.CTkEntry(
            sidebar, height=38, corner_radius=10,
            fg_color=INPUT, border_color=BORDER, text_color=TEXT
        )
        self.entry_chars.insert(0, self.config.get("chars", "400"))
        self.entry_chars.pack(fill="x", padx=20, pady=(5, 10))

        self._field_label(sidebar, "Interwał wysyłania [s]")
        self.entry_interval = ctk.CTkEntry(
            sidebar, height=38, corner_radius=10,
            fg_color=INPUT, border_color=BORDER, text_color=TEXT
        )
        self.entry_interval.insert(0, self.config.get("interval", "60"))
        self.entry_interval.pack(fill="x", padx=20, pady=(5, 10))

        self._field_label(sidebar, "Sposób wysyłania")
        self.method_menu = ctk.CTkOptionMenu(
            sidebar,
            values=[
                "Pynput Mode (najlepszy)",
                "Direct Unicode (bez wklejania)",
                "Symulacja pisania",
                "Wklej: Shift+Insert",
                "Wklej: Ctrl+V"
            ],
            height=38, corner_radius=10,
            fg_color="#0B1730",
            button_color="#112A49",
            button_hover_color="#16395F",
            text_color=TEXT
        )
        self.method_menu.set(self.config.get("method", "Pynput Mode (najlepszy)"))
        self.method_menu.pack(fill="x", padx=20, pady=(5, 10))

        self._field_label(sidebar, "Prędkość pisania")
        self.speed_menu = ctk.CTkOptionMenu(
            sidebar,
            values=["Szybko (0.015s)", "Naturalnie (0.05s)", "Wolno (0.1s)"],
            height=38, corner_radius=10,
            fg_color="#0B1730",
            button_color="#112A49",
            button_hover_color="#16395F",
            text_color=TEXT
        )
        self.speed_menu.set(self.config.get("speed", "Naturalnie (0.05s)"))
        self.speed_menu.pack(fill="x", padx=20, pady=(5, 14))

        ctk.CTkButton(
            sidebar,
            text="ZAPISZ USTAWIENIA",
            command=self.save_config,
            height=38,
            corner_radius=10,
            fg_color="#10192C",
            hover_color="#18253E",
            border_width=1,
            border_color=BORDER,
            text_color=MUTED,
            font=("Segoe UI", 10, "bold")
        ).pack(fill="x", padx=20, pady=(8, 8))

        self.btn_toggle = ctk.CTkButton(
            sidebar,
            text="▶  URUCHOM BOTA",
            command=self.toggle_bot,
            height=52,
            corner_radius=12,
            fg_color=CYAN,
            hover_color=ACCENT_HOVER,
            text_color="#001018",
            font=("Segoe UI", 15, "bold")
        )
        self.btn_toggle.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkButton(
            sidebar,
            text="⚡  WYŚLIJ TEST",
            command=self.send_test_message,
            height=42,
            corner_radius=12,
            fg_color="#0B1730",
            hover_color="#132947",
            border_width=1,
            border_color=PURPLE,
            text_color="#D9C6FF",
            font=("Segoe UI", 12, "bold")
        ).pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkButton(
            sidebar,
            text="＋  WŁASNE ŹRÓDŁA",
            command=self.open_custom_sources_manager,
            height=42,
            corner_radius=12,
            fg_color="#10162A",
            hover_color="#18233F",
            border_width=1,
            border_color=GREEN,
            text_color=GREEN,
            font=("Segoe UI", 11, "bold")
        ).pack(fill="x", padx=20, pady=(0, 12))

        info = ctk.CTkFrame(
            sidebar,
            fg_color="#081120",
            border_width=1,
            border_color="#14345A",
            corner_radius=12
        )
        info.pack(fill="x", padx=20, pady=(8, 0))

        ctk.CTkLabel(
            info,
            text="TRYB PYNPUT",
            font=("Consolas", 10, "bold"),
            text_color=GREEN
        ).pack(anchor="w", padx=12, pady=(10, 1))

        ctk.CTkLabel(
            info,
            text="Polecany do czatu blokującego wklejanie.\nNie korzysta ze schowka.",
            justify="left",
            font=("Segoe UI", 9),
            text_color=MUTED
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def _field_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 11, "bold"), text_color=MUTED).pack(anchor="w", padx=18, pady=(10, 5))

    def build_main(self):
        main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        main.grid(row=1, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        summary = ctk.CTkFrame(main, fg_color="transparent")
        summary.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 12))

        for i in range(4):
            summary.grid_columnconfigure(i, weight=1)

        self.card_sources = self._summary_card(summary, 0, "ŹRÓDŁA DANYCH", str(30 + len(self.custom_sources)) + "+", CYAN)
        self.card_interval = self._summary_card(summary, 1, "INTERWAŁ", f"{self.config.get('interval','60')} s", PURPLE)
        self.card_limit = self._summary_card(summary, 2, "LIMIT TEKSTU", f"{self.config.get('chars','400')} znaków", MAGENTA)
        self.card_engine = self._summary_card(summary, 3, "SILNIK WEJŚCIA", "PYNPUT", GREEN)

        panel = ctk.CTkFrame(
            main,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        panel.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))

        ctk.CTkLabel(
            panel,
            text="MATRYCA ŹRÓDEŁ",
            font=("Consolas", 12, "bold"),
            text_color=CYAN
        ).pack(anchor="w", padx=16, pady=(14, 8))

        scroll = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_button_color="#173052",
            scrollbar_button_hover_color="#24527C"
        )
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        groups = [
            ("RYNEK", [
                ("Bitcoin (BTC)", self.var_btc),
                ("Ethereum (ETH)", self.var_eth),
                ("Solana (SOL)", self.var_sol),
                ("Dogecoin (DOGE)", self.var_doge),
                ("Kursy NBP", self.var_nbp),
                ("RMF24 Ekonomia", self.var_rmf_economy),
            ]),
            ("POLSKA", [
                ("Pogoda", self.var_weather),
                ("Jakość powietrza", self.var_air),
                ("Indeks UV", self.var_uv),
                ("Wiadomości Google", self.var_news),
                ("RMF24", self.var_rmf_main),
                ("Historia dnia", self.var_history),
                ("Ciekawostki", self.var_trivia),
            ]),
            ("ŚWIAT", [
                ("RMF24 Świat", self.var_rmf_world),
                ("Trzęsienia ziemi", self.var_earthquake),
                ("Bałtyk / fale", self.var_marine),
            ]),
            ("TECHNOLOGIA / CYBER", [
                ("Cyberbezpieczeństwo", self.var_cyber),
                ("Antyweb / Tech", self.var_antyweb),
                ("Hacker News", self.var_hackernews),
                ("Ars Technica", self.var_ars),
                ("GitHub Live", self.var_github_events),
            ]),
            ("NAUKA / KOSMOS", [
                ("NASA", self.var_nasa),
                ("Pozycja ISS", self.var_iss),
                ("RMF24 Nauka", self.var_rmf_science),
            ]),
            ("STATUS USŁUG", [
                ("GitHub Status", self.var_github_status),
                ("OpenAI Status", self.var_openai_status),
                ("Cloudflare Status", self.var_cloudflare_status),
            ]),
            ("ROZRYWKA", [
                ("Darmowe gry PC", self.var_freegames),
                ("RMF24 Sport", self.var_rmf_sport),
                ("Losowy żart", self.var_joke),
            ]),
        ]

        for group_name, entries in groups:
            group = ctk.CTkFrame(
                scroll,
                fg_color="#0A1323",
                corner_radius=12,
                border_width=1,
                border_color="#172942"
            )
            group.pack(fill="x", padx=4, pady=6)

            ctk.CTkLabel(
                group,
                text=group_name,
                font=("Consolas", 10, "bold"),
                text_color="#8FB7D9"
            ).pack(anchor="w", padx=12, pady=(9, 4))

            grid = ctk.CTkFrame(group, fg_color="transparent")
            grid.pack(fill="x", padx=8, pady=(0, 8))
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)

            for idx, (label, var) in enumerate(entries):
                ctk.CTkSwitch(
                    grid,
                    text=label,
                    variable=var,
                    font=("Segoe UI", 10),
                    text_color=TEXT,
                    progress_color=CYAN,
                    button_color="#D7F9FF",
                    button_hover_color="#FFFFFF"
                ).grid(
                    row=idx // 2,
                    column=idx % 2,
                    sticky="w",
                    padx=8,
                    pady=6
                )

        custom_count = sum(1 for var in self.custom_source_vars if var.get())
        custom_panel = ctk.CTkFrame(
            scroll,
            fg_color="#0A1323",
            corner_radius=12,
            border_width=1,
            border_color=GREEN
        )
        custom_panel.pack(fill="x", padx=4, pady=6)

        custom_header = ctk.CTkFrame(custom_panel, fg_color="transparent")
        custom_header.pack(fill="x", padx=12, pady=(9, 4))

        self.custom_sources_label = ctk.CTkLabel(
            custom_header,
            text=f"WŁASNE ŹRÓDŁA ({custom_count}/{len(self.custom_sources)} aktywnych)",
            font=("Consolas", 10, "bold"),
            text_color=GREEN
        )
        self.custom_sources_label.pack(side="left")

        if self.custom_sources:
            quick_buttons = ctk.CTkFrame(custom_header, fg_color="transparent")
            quick_buttons.pack(side="right")

            ctk.CTkButton(
                quick_buttons,
                text="WŁĄCZ WSZYSTKIE",
                width=100,
                height=26,
                command=lambda: self.set_all_custom_sources(True),
                fg_color="#123120",
                hover_color="#19432C",
                text_color=GREEN,
                font=("Segoe UI", 8, "bold")
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                quick_buttons,
                text="WYŁĄCZ",
                width=68,
                height=26,
                command=lambda: self.set_all_custom_sources(False),
                fg_color="#30131D",
                hover_color="#481C2B",
                text_color="#FF799B",
                font=("Segoe UI", 8, "bold")
            ).pack(side="left")

        if not self.custom_sources:
            ctk.CTkLabel(
                custom_panel,
                text="Brak własnych źródeł. Dodaj je przyciskiem „WŁASNE ŹRÓDŁA” po lewej.",
                font=("Segoe UI", 9),
                text_color=MUTED
            ).pack(anchor="w", padx=12, pady=(0, 9))
        else:
            custom_grid = ctk.CTkFrame(custom_panel, fg_color="transparent")
            custom_grid.pack(fill="x", padx=8, pady=(0, 8))
            custom_grid.grid_columnconfigure(0, weight=1)
            custom_grid.grid_columnconfigure(1, weight=1)

            for index, source in enumerate(self.custom_sources):
                label = source.get("name", f"Źródło {index + 1}")
                source_type = source.get("type", "RSS")

                ctk.CTkSwitch(
                    custom_grid,
                    text=f"{label}  [{source_type}]",
                    variable=self.custom_source_vars[index],
                    command=self.on_custom_source_toggle,
                    font=("Segoe UI", 10),
                    text_color=TEXT,
                    progress_color=GREEN,
                    button_color="#D7FFE8",
                    button_hover_color="#FFFFFF"
                ).grid(
                    row=index // 2,
                    column=index % 2,
                    sticky="w",
                    padx=8,
                    pady=6
                )

        log_card = ctk.CTkFrame(
            main,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )
        log_card.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(log_card, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))
        head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            head,
            text="DZIENNIK AKTYWNOŚCI",
            font=("Consolas", 11, "bold"),
            text_color=GREEN
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            head,
            text="WYCZYŚĆ",
            command=self.clear_log,
            width=80,
            height=28,
            corner_radius=8,
            fg_color="#10192A",
            hover_color="#18253B",
            border_width=1,
            border_color=BORDER,
            text_color=MUTED,
            font=("Consolas", 9, "bold")
        ).grid(row=0, column=1, sticky="e")

        self.log_box = ctk.CTkTextbox(
            log_card,
            fg_color="#050B14",
            border_width=0,
            text_color="#9FE7C4",
            font=("Consolas", 10),
            corner_radius=10
        )
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.log_box.insert(
            "end",
            f"{APP_NAME} {APP_VERSION}\n"
            "Interfejs gotowy.\n"
            "Silnik Pynput gotowy do pracy.\n\n"
        )
        self.log_box.configure(state="disabled")

    def _summary_card(self, parent, column, title, value, accent):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            corner_radius=14,
            border_width=1,
            border_color="#1B2A43"
        )
        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(0 if column == 0 else 6, 0)
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Consolas", 9, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=14, pady=(10, 0))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 21, "bold"),
            text_color=accent
        )
        value_label.pack(anchor="w", padx=14, pady=(2, 10))
        return value_label

    def update_status(self, running):
        if running:
            self.status_badge.configure(
                text="●  BOT AKTYWNY",
                text_color=GREEN,
                fg_color="#071A13"
            )
            self.btn_toggle.configure(
                text="■  ZATRZYMAJ BOTA",
                fg_color="#30101D",
                hover_color="#481828",
                text_color="#FF7A9F"
            )
        else:
            self.status_badge.configure(
                text="●  BOT WYŁĄCZONY",
                text_color=RED,
                fg_color="#170B16"
            )
            self.btn_toggle.configure(
                text="▶  URUCHOM BOTA",
                fg_color=CYAN,
                hover_color=ACCENT_HOVER,
                text_color="#001018"
            )

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
        if "0.015s" in value:
            return 0.015
        if "0.1s" in value:
            return 0.1
        return 0.05

    def send_message_to_active_field(self, msg):
        """Wysyła tekst do aktualnie aktywnego pola tekstowego."""
        method = self.method_menu.get()
        time.sleep(0.15)

        if "Pynput Mode" in method:
            # Ten sam mechanizm co w starym, działającym programie użytkownika.
            pynput_keyboard.type(msg)
            time.sleep(0.10)
            pynput_keyboard.press(Key.enter)
            pynput_keyboard.release(Key.enter)
            return

        if "Direct Unicode" in method:
            type_unicode_windows(msg, delay=self.get_typing_delay())

        elif "Symulacja pisania" in method:
            keyboard.write(
                usun_polskie_znaki(msg),
                delay=self.get_typing_delay()
            )

        else:
            pyperclip.copy(msg)
            time.sleep(0.10)

            if "Ctrl+V" in method:
                pyautogui.hotkey("ctrl", "v")
            else:
                pyautogui.hotkey("shift", "insert")

        time.sleep(0.15)
        pyautogui.press("enter")

    def send_test_message(self):
        self.write_log("TEST: masz 3 sekundy, kliknij docelowe pole tekstowe.")

        def worker():
            for i in range(3, 0, -1):
                self.write_log(f"Test za {i}s...")
                time.sleep(1)

            try:
                msg = f"{get_current_time()} | InfoPulse PL — test wysyłania"
                self.send_message_to_active_field(msg)
                self.write_log("TEST OK: próba wysyłania wykonana.")
            except Exception as e:
                self.write_log(f"TEST BŁĄD: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def on_custom_source_toggle(self):
        """Obsługuje przełączenie własnego źródła w głównym menu."""
        self.sync_custom_source_states()
        active = sum(
            1 for source in self.custom_sources
            if source.get("enabled", True)
        )

        if hasattr(self, "custom_sources_label"):
            self.custom_sources_label.configure(
                text=f"WŁASNE ŹRÓDŁA ({active}/{len(self.custom_sources)} aktywnych)"
            )

        self.save_config()
        self.write_log(
            f"Własne źródła: aktywne {active}/{len(self.custom_sources)}."
        )

    def set_all_custom_sources(self, state):
        """Włącza lub wyłącza wszystkie własne źródła."""
        for var in self.custom_source_vars:
            var.set(state)

        self.on_custom_source_toggle()

    def rebuild_custom_source_vars(self):
        """Odtwarza przełączniki po dodaniu/usunięciu źródeł."""
        self.custom_source_vars = [
            ctk.BooleanVar(value=source.get("enabled", True))
            for source in self.custom_sources
        ]

    def open_custom_sources_manager(self):
        window = ctk.CTkToplevel(self)
        window.title("InfoPulse — Własne źródła")
        window.geometry("980x720")
        window.minsize(820, 620)
        window.configure(fg_color=BG)
        window.transient(self)
        window.grab_set()

        # Lepsze zachowanie na różnych monitorach.
        try:
            sw = window.winfo_screenwidth()
            sh = window.winfo_screenheight()
            width = min(1080, max(860, int(sw * 0.72)))
            height = min(780, max(640, int(sh * 0.78)))
            x = max(0, (sw - width) // 2)
            y = max(0, (sh - height) // 2)
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        header = ctk.CTkFrame(window, fg_color="#070B16", corner_radius=0, height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="WŁASNE ŹRÓDŁA",
            font=("Segoe UI", 22, "bold"),
            text_color=TEXT
        ).pack(anchor="w", padx=22, pady=(15, 0))

        ctk.CTkLabel(
            header,
            text="RSS / Atom / JSON API GET • dodawaj, testuj i zarządzaj źródłami bez edycji kodu",
            font=("Segoe UI", 10),
            text_color=CYAN
        ).pack(anchor="w", padx=22, pady=(2, 10))

        body = ctk.CTkFrame(window, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=18)
        body.grid_columnconfigure(0, weight=2, minsize=280)
        body.grid_columnconfigure(1, weight=3, minsize=420)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(
            body,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER,
            corner_radius=14
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right = ctk.CTkFrame(
            body,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER,
            corner_radius=14
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # -------- Lewa kolumna: lista źródeł --------
        top_left = ctk.CTkFrame(left, fg_color="transparent")
        top_left.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            top_left,
            text="ZAPISANE ŹRÓDŁA",
            font=("Consolas", 10, "bold"),
            text_color=CYAN
        ).pack(side="left")

        source_counter = ctk.CTkLabel(
            top_left,
            text=str(len(self.custom_sources)),
            font=("Consolas", 10, "bold"),
            text_color=GREEN,
            fg_color="#071A13",
            corner_radius=8,
            padx=8,
            pady=3
        )
        source_counter.pack(side="right")

        search_entry = ctk.CTkEntry(
            left,
            placeholder_text="Szukaj źródła...",
            fg_color=INPUT,
            border_color=BORDER,
            height=34
        )
        search_entry.pack(fill="x", padx=12, pady=(0, 8))

        list_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        selected_index = {"value": None}

        # -------- Prawa kolumna: przewijany formularz --------
        ctk.CTkLabel(
            right,
            text="EDYCJA ŹRÓDŁA",
            font=("Consolas", 10, "bold"),
            text_color=PURPLE
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        form = ctk.CTkScrollableFrame(
            right,
            fg_color="transparent",
            scrollbar_button_color="#173052",
            scrollbar_button_hover_color="#24527C"
        )
        form.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        form.grid_columnconfigure(0, weight=1)

        def add_label(text):
            ctk.CTkLabel(
                form,
                text=text,
                font=("Segoe UI", 9),
                text_color=MUTED
            ).pack(anchor="w", padx=8, pady=(7, 3))

        name_entry = ctk.CTkEntry(
            form,
            placeholder_text="np. Sekurak",
            fg_color=INPUT,
            border_color=BORDER,
            height=36
        )
        add_label("Nazwa źródła")
        name_entry.pack(fill="x", padx=8)

        type_menu = ctk.CTkOptionMenu(
            form,
            values=["RSS", "ATOM", "JSON API"],
            fg_color="#0B1730",
            button_color="#112A49",
            button_hover_color="#16395F",
            height=36
        )
        add_label("Typ źródła")
        type_menu.pack(fill="x", padx=8)

        url_entry = ctk.CTkEntry(
            form,
            placeholder_text="https://example.com/feed",
            fg_color=INPUT,
            border_color=BORDER,
            height=36
        )
        add_label("Adres URL")
        url_entry.pack(fill="x", padx=8)

        prefix_entry = ctk.CTkEntry(
            form,
            placeholder_text="np. Cyber",
            fg_color=INPUT,
            border_color=BORDER,
            height=36
        )
        add_label("Prefiks wiadomości")
        prefix_entry.pack(fill="x", padx=8)

        path_entry = ctk.CTkEntry(
            form,
            placeholder_text="np. data.0.title",
            fg_color=INPUT,
            border_color=BORDER,
            height=36
        )
        add_label("Ścieżka JSON (tylko API, opcjonalna)")
        path_entry.pack(fill="x", padx=8)

        add_label('Nagłówki HTTP jako JSON (opcjonalne), np. {"X-Api-Key":"..."}')
        headers_entry = ctk.CTkTextbox(
            form,
            height=86,
            fg_color=INPUT,
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
            font=("Consolas", 10)
        )
        headers_entry.pack(fill="x", padx=8)

        enabled_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            form,
            text="Źródło aktywne",
            variable=enabled_var,
            progress_color=GREEN
        ).pack(anchor="w", padx=8, pady=(10, 6))

        # Podgląd wyniku testu – bez szukania w głównym logu.
        add_label("Podgląd testu")
        preview_box = ctk.CTkTextbox(
            form,
            height=95,
            fg_color="#050B14",
            border_width=1,
            border_color="#173052",
            corner_radius=8,
            text_color="#B8F5D0",
            font=("Consolas", 10)
        )
        preview_box.pack(fill="x", padx=8, pady=(0, 8))
        preview_box.insert("1.0", "Tutaj pojawi się wynik testu źródła.")
        preview_box.configure(state="disabled")

        def set_preview(text):
            preview_box.configure(state="normal")
            preview_box.delete("1.0", "end")
            preview_box.insert("1.0", text)
            preview_box.configure(state="disabled")

        def clear_form():
            selected_index["value"] = None
            for entry in (name_entry, url_entry, prefix_entry, path_entry):
                entry.delete(0, "end")
            headers_entry.delete("1.0", "end")
            type_menu.set("RSS")
            enabled_var.set(True)
            set_preview("Nowe źródło — uzupełnij dane i kliknij TESTUJ.")

        def load_source(index):
            if index < 0 or index >= len(self.custom_sources):
                return

            selected_index["value"] = index
            source = self.custom_sources[index]

            name_entry.delete(0, "end")
            name_entry.insert(0, source.get("name", ""))

            type_menu.set(source.get("type", "RSS"))

            url_entry.delete(0, "end")
            url_entry.insert(0, source.get("url", ""))

            prefix_entry.delete(0, "end")
            prefix_entry.insert(0, source.get("prefix", ""))

            path_entry.delete(0, "end")
            path_entry.insert(0, source.get("json_path", ""))

            headers_entry.delete("1.0", "end")
            headers = source.get("headers", {})
            if headers:
                headers_entry.insert("1.0", json.dumps(headers, ensure_ascii=False, indent=2))

            enabled_var.set(source.get("enabled", True))
            set_preview(f"Wybrano: {source.get('name', 'Bez nazwy')}")

        def refresh_list(*_):
            for child in list_frame.winfo_children():
                child.destroy()

            query = search_entry.get().strip().lower()
            visible = []

            for index, source in enumerate(self.custom_sources):
                haystack = f"{source.get('name','')} {source.get('type','')} {source.get('url','')}".lower()
                if query and query not in haystack:
                    continue
                visible.append((index, source))

            source_counter.configure(text=str(len(self.custom_sources)))

            if not visible:
                ctk.CTkLabel(
                    list_frame,
                    text="Brak pasujących źródeł.",
                    text_color=MUTED
                ).pack(pady=20)
                return

            for index, source in visible:
                active = "●" if source.get("enabled", True) else "○"
                color = GREEN if source.get("enabled", True) else MUTED

                ctk.CTkButton(
                    list_frame,
                    text=f"{active}  {source.get('name','Bez nazwy')}\n    {source.get('type','RSS')}",
                    command=lambda i=index: load_source(i),
                    anchor="w",
                    height=48,
                    fg_color="#0D1729",
                    hover_color="#14233B",
                    text_color=color,
                    font=("Segoe UI", 10, "bold")
                ).pack(fill="x", pady=3)

        search_entry.bind("<KeyRelease>", refresh_list)

        def collect_form_source():
            name = name_entry.get().strip()
            url = url_entry.get().strip()

            if not name or not url:
                set_preview("BŁĄD: nazwa i adres URL są wymagane.")
                return None

            headers_text = headers_entry.get("1.0", "end").strip()
            try:
                headers = json.loads(headers_text) if headers_text else {}
                if not isinstance(headers, dict):
                    raise ValueError
            except Exception:
                set_preview("BŁĄD: nagłówki HTTP muszą być poprawnym obiektem JSON.")
                return None

            return {
                "name": name,
                "type": type_menu.get().strip(),
                "url": url,
                "prefix": prefix_entry.get().strip() or name,
                "json_path": path_entry.get().strip(),
                "headers": headers,
                "enabled": enabled_var.get(),
            }

        def save_source():
            source = collect_form_source()
            if not source:
                return

            index = selected_index["value"]
            if index is None:
                self.custom_sources.append(source)
                self.write_log(f"Dodano własne źródło: {source['name']}")
                set_preview("Źródło zostało dodane i zapisane.")
            else:
                self.custom_sources[index] = source
                self.write_log(f"Zaktualizowano własne źródło: {source['name']}")
                set_preview("Zmiany zostały zapisane.")

            self.rebuild_custom_source_vars()
            self.save_config()
            self.card_sources.configure(text=str(30 + len(self.custom_sources)) + "+")
            refresh_list()

        def remove_source():
            index = selected_index["value"]
            if index is None:
                set_preview("Najpierw wybierz źródło z listy po lewej.")
                return

            name = self.custom_sources[index].get("name", "źródło")
            del self.custom_sources[index]
            self.rebuild_custom_source_vars()
            self.save_config()
            self.card_sources.configure(text=str(30 + len(self.custom_sources)) + "+")
            self.write_log(f"Usunięto własne źródło: {name}")
            clear_form()
            refresh_list()

        def duplicate_source():
            index = selected_index["value"]
            if index is None:
                set_preview("Najpierw wybierz źródło do skopiowania.")
                return

            source = dict(self.custom_sources[index])
            source["name"] = source.get("name", "Źródło") + " — kopia"
            self.custom_sources.append(source)
            self.rebuild_custom_source_vars()
            self.save_config()
            self.card_sources.configure(text=str(30 + len(self.custom_sources)) + "+")
            refresh_list()
            set_preview("Utworzono kopię źródła.")

        def test_source():
            source = collect_form_source()
            if not source:
                return

            set_preview("Testuję źródło...")

            def worker():
                result = get_custom_source(source)
                self.write_log(f"TEST ŹRÓDŁA → {result}")
                self.after(0, lambda: set_preview(result))

            threading.Thread(target=worker, daemon=True).start()

        # Pasek akcji przypięty na dole — zawsze widoczny.
        action_bar = ctk.CTkFrame(
            right,
            fg_color="#07101D",
            corner_radius=10,
            border_width=1,
            border_color="#172942"
        )
        action_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        for col in range(3):
            action_bar.grid_columnconfigure(col, weight=1)

        ctk.CTkButton(
            action_bar,
            text="＋ NOWE",
            command=clear_form,
            fg_color="#16213A",
            hover_color="#203152",
            height=36
        ).grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=(8, 4))

        ctk.CTkButton(
            action_bar,
            text="⚡ TESTUJ",
            command=test_source,
            fg_color=PURPLE,
            hover_color="#7841D0",
            height=36
        ).grid(row=0, column=1, sticky="ew", padx=4, pady=(8, 4))

        ctk.CTkButton(
            action_bar,
            text="✓ ZAPISZ",
            command=save_source,
            fg_color=GREEN,
            hover_color="#2DD477",
            text_color="#00150B",
            height=36
        ).grid(row=0, column=2, sticky="ew", padx=(4, 8), pady=(8, 4))

        ctk.CTkButton(
            action_bar,
            text="⧉ DUPLIKUJ",
            command=duplicate_source,
            fg_color="#12314A",
            hover_color="#194463",
            height=34
        ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=(8, 4), pady=(4, 8))

        ctk.CTkButton(
            action_bar,
            text="✕ USUŃ",
            command=remove_source,
            fg_color="#35101D",
            hover_color="#50182A",
            text_color="#FF799B",
            height=34
        ).grid(row=1, column=2, sticky="ew", padx=(4, 8), pady=(4, 8))

        refresh_list()

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
            self.write_log(f"Start za {i} s... Kliknij pole tekstowe w oknie docelowym.")
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
                if self.var_iss.get(): informacje.append(get_iss_position_v3())
                if self.var_history.get(): informacje.append(get_on_this_day())
                if self.var_freegames.get(): informacje.append(get_free_games())
                if self.var_cyber.get(): informacje.append(get_cyber_news(self.wyslane_cyber))
                if self.var_earthquake.get(): informacje.append(get_earthquakes())
                if self.var_antyweb.get(): informacje.append(get_antyweb_news(self.wyslane_anty))
                if self.var_nasa.get(): informacje.append(get_nasa_news())
                if self.var_hackernews.get(): informacje.append(get_hackernews())
                if self.var_uv.get(): informacje.append(get_uv_index(self.voivodeship_index))
                if self.var_marine.get(): informacje.append(get_marine_conditions())
                if self.var_rmf_main.get(): informacje.append(get_rss_item("rmf_main"))
                if self.var_rmf_world.get(): informacje.append(get_rss_item("rmf_world"))
                if self.var_rmf_economy.get(): informacje.append(get_rss_item("rmf_economy"))
                if self.var_rmf_science.get(): informacje.append(get_rss_item("rmf_science"))
                if self.var_rmf_sport.get(): informacje.append(get_rss_item("rmf_sport"))
                if self.var_ars.get(): informacje.append(get_rss_item("ars"))
                if self.var_github_status.get(): informacje.append(get_service_status("github_status"))
                if self.var_openai_status.get(): informacje.append(get_service_status("openai_status"))
                if self.var_cloudflare_status.get(): informacje.append(get_service_status("cloudflare_status"))
                if self.var_github_events.get(): informacje.append(get_github_trending_events())
                if self.var_joke.get(): informacje.append(get_random_joke())
                self.sync_custom_source_states()
                for source in self.custom_sources:
                    if source.get("enabled", True):
                        informacje.append(get_custom_source(source))
                cleaned = [wyczysc_tekst(x) for x in informacje if x]
                random.shuffle(cleaned)
                msg = f"{get_current_time()} | " + " | ".join(cleaned) if cleaned else get_current_time()
                msg = inteligentne_ucinanie(msg, self.max_chars)
                self.send_message_to_active_field(msg)
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
