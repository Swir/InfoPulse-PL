<div align="center">

# 📡 InfoPulse PL v3.2 MAX

### Futurystyczny agregator informacji, dashboard desktopowy i automat do wysyłania wiadomości w Pythonie

**Wiadomości • Pogoda • Krypto • Cyber • Kosmos • RSS • API • AutoChat**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-00E5FF)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![Version](https://img.shields.io/badge/Version-3.2%20MAX-9B5CFF)
![Status](https://img.shields.io/badge/Status-Active-39FF88)

</div>

---

## 🚀 O projekcie

**InfoPulse PL** zbiera informacje z wielu publicznych API i kanałów RSS/Atom, składa je w krótką wiadomość i może wpisać ją do aktualnie aktywnego pola tekstowego. Program ma polski, gamingowo-futurystyczny interfejs zbudowany w **CustomTkinter** i został zaprojektowany przede wszystkim pod Windows.

W wersji **3.2 MAX** aplikacja obsługuje również własne źródła użytkownika: RSS, Atom oraz JSON API GET. Każde własne źródło można włączać i wyłączać bezpośrednio z głównego dashboardu.

---

## ✨ Najważniejsze funkcje

| Kategoria | Źródła / funkcje |
|---|---|
| 📰 Wiadomości | Google News PL, RMF24 i dodatkowe kanały RSS |
| 🛡️ Cyber / Tech | Niebezpiecznik, Antyweb, Hacker News, Ars Technica, GitHub Live |
| 🌦️ Pogoda | Open-Meteo dla polskich regionów |
| 🌫️ Środowisko | jakość powietrza, PM10, AQI, indeks UV |
| 🌊 Morze | warunki na Bałtyku / fale |
| 💱 Waluty | NBP USD / EUR / GBP |
| ₿ Krypto | BTC, ETH, SOL, DOGE przez Binance |
| 🚀 Kosmos | NASA oraz aktualna pozycja ISS |
| 🌍 Ziemia | trzęsienia ziemi USGS |
| 🎮 Gry | darmowe gry PC z GamerPower |
| 📚 Wiedza | Wikipedia — ciekawostki i wydarzenia historyczne |
| 🟢 Status usług | GitHub, OpenAI, Cloudflare |
| ➕ Własne źródła | RSS, Atom i JSON API GET z własnymi nagłówkami |
| ⌨️ Wysyłanie | Pynput Mode, Direct Unicode, Ctrl+V, Shift+Insert, symulacja pisania |
| ⚙️ Konfiguracja | ustawienia i własne źródła zapisywane lokalnie w JSON |

---

## 🎛️ Własne źródła RSS / API

Menedżer **WŁASNE ŹRÓDŁA** pozwala bez edycji kodu:

- dodać kanał **RSS** lub **Atom**,
- dodać **JSON API GET**,
- ustawić własną nazwę i prefiks wiadomości,
- wskazać ścieżkę JSON, np. `data.0.title`,
- dodać opcjonalne nagłówki HTTP w formacie JSON,
- przetestować źródło przed użyciem,
- wyszukiwać, edytować, duplikować i usuwać źródła,
- włączać i wyłączać każde własne źródło z głównego menu,
- jednym kliknięciem włączyć lub wyłączyć wszystkie własne źródła.

> Jeśli API wymaga klucza, można przekazać go jako nagłówek, np. `{"X-Api-Key":"TWÓJ_KLUCZ"}`. Nie publikuj prywatnych kluczy API w repozytorium.

---

## ⌨️ Pynput Mode

Domyślnym i polecanym trybem jest **Pynput Mode (najlepszy)**. Program wpisuje wiadomość jak klawiatura, bez konieczności korzystania ze schowka, a następnie naciska Enter.

Dostępne są również:

- `Direct Unicode (bez wklejania)`,
- `Symulacja pisania`,
- `Wklej: Shift+Insert`,
- `Wklej: Ctrl+V`.

---

## 🖥️ Interfejs

InfoPulse PL v3.2 MAX posiada ciemny, neonowy dashboard z:

- polskim **Centrum Dowodzenia**,
- statusem `BOT AKTYWNY / BOT WYŁĄCZONY`,
- kartami źródeł, interwału, limitu tekstu i silnika wejścia,
- pogrupowaną matrycą źródeł,
- osobną sekcją własnych RSS/API z przełącznikami ON/OFF,
- responsywnym menedżerem własnych źródeł,
- wyszukiwarką źródeł i podglądem testów,
- dziennikiem aktywności.

---

## 📦 Instalacja

### 1. Pobierz repozytorium

```bash
git clone https://github.com/Swir/InfoPulse-PL.git
cd InfoPulse-PL
```

### 2. Zainstaluj biblioteki

```bash
pip install -r requirements.txt
```

### 3. Uruchom program

```bash
python InfoPulse_PL.py
```

---

## ⚙️ Jak działa

```text
Publiczne API / RSS / Atom / własne JSON API
                    │
                    ▼
              InfoPulse PL
                    │
       ┌────────────┼────────────┐
       │            │            │
  wybór źródeł   limit tekstu   interwał
       │            │            │
       └────────────┼────────────┘
                    ▼
          składanie wiadomości
                    │
                    ▼
       Pynput / Direct Unicode / paste
                    │
                    ▼
          aktywne pole tekstowe
```

---

## 🔧 Główne ustawienia

| Ustawienie | Opis |
|---|---|
| Limit znaków | maksymalna długość jednej wiadomości |
| Interwał | czas pomiędzy kolejnymi wiadomościami |
| Sposób wysyłania | Pynput, Direct Unicode, symulacja lub wklejanie |
| Prędkość pisania | szybko / naturalnie / wolno |
| Źródła | osobne przełączniki dla każdego modułu |
| Własne źródła | niezależne przełączniki RSS/API w głównym menu |

Ustawienia są przechowywane lokalnie w pliku `infopulse_config.json` obok programu.

---

## 🛠️ Technologie

- Python
- CustomTkinter
- Requests
- Pynput
- PyAutoGUI
- Pyperclip
- Keyboard
- XML / RSS / Atom
- Open-Meteo
- Binance API
- NBP API
- NASA RSS
- Hacker News API
- USGS
- Wikipedia API
- GitHub Status / Events

---

## ⚠️ Odpowiedzialne użycie

InfoPulse PL automatyzuje wpisywanie tekstu do aktualnie aktywnego pola. Używaj automatyzacji tam, gdzie jest to dozwolone. Nie wykorzystuj programu do spamu, floodowania ani wysyłania niechcianych wiadomości. Zewnętrzne API i kanały RSS mogą zmieniać format lub być czasowo niedostępne.

---

## 👨‍💻 Autor

Developed by **Swir** — [@Swir](https://github.com/Swir)

---

<div align="center">

### 📡 Jedno centrum. Dziesiątki strumieni informacji.

**Zbieraj • Łącz • Wysyłaj**

⭐ Jeśli projekt Ci się podoba, zostaw gwiazdkę!

</div>
