<div align="center">

# 📡 InfoPulse PL

### Polish information aggregator, desktop dashboard and auto-posting assistant built with Python

**News • Weather • Crypto • Technology • Space • Market Data**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-1F6AA5)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![Language](https://img.shields.io/badge/Language-Polish-DC143C)
![Status](https://img.shields.io/badge/Status-Active-success)

</div>

---

## 🚀 About

**InfoPulse PL** is a modern Python desktop information dashboard that collects data from multiple public sources and combines selected items into compact messages. It is designed as a Polish information aggregator for users who want one interface for news, weather, cryptocurrency prices, exchange rates, technology headlines, space updates and other live information.

The application can prepare and send the generated information to the currently focused text field using clipboard paste or simulated keyboard typing.

---

## ✨ Features

| Category | Sources / Functions |
|---|---|
| 📰 News | Google News Poland, Antyweb, Hacker News |
| 🛡️ Cybersecurity | Niebezpiecznik RSS |
| 🌦️ Weather | Open-Meteo weather for Polish regions |
| 🌫️ Air quality | European AQI and PM10 |
| 💱 Exchange rates | NBP USD / EUR / GBP |
| ₿ Crypto | BTC, ETH, SOL and DOGE via Binance |
| 🚀 Space | NASA news and ISS position |
| 🌍 Earth | USGS earthquake data |
| 🎮 Gaming | Free PC game offers |
| 📚 Knowledge | Polish Wikipedia random facts and historical events |
| ⌨️ Output | Ctrl+V, Shift+Insert or typing simulation |
| ⚙️ Configuration | Persistent JSON settings |

---

## 🖥️ Interface

InfoPulse PL uses a modern dark dashboard built with **CustomTkinter**. The redesigned interface includes:

- clear `ACTIVE / STOPPED` status,
- separate control panel,
- grouped information sources,
- activity log,
- current interval and message-length cards,
- clean Windows-friendly layout.

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Swir/InfoPulse-PL.git
cd InfoPulse-PL
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run InfoPulse PL

```bash
python InfoPulse_PL_v2.py
```

---

## ⚙️ How It Works

```text
Public APIs / RSS feeds
          │
          ▼
     InfoPulse PL
          │
          ├── Select enabled modules
          ├── Build compact information message
          ├── Apply character limit
          │
          ▼
Clipboard paste / keyboard simulation
          │
          ▼
Currently focused text field
```

---

## 🔧 Main Settings

| Setting | Description |
|---|---|
| Message length | Maximum number of characters in one generated message |
| Interval | Delay between generated messages |
| Output method | Shift+Insert, Ctrl+V or simulated typing |
| Typing speed | Fast, natural or slow typing simulation |
| Sources | Enable or disable individual information modules |

Settings are stored locally in `ghost_config.json` next to the application.

---

## 🔍 Discoverability

Common search terms related to this project:

`polish news bot` • `python information aggregator` • `python news dashboard` • `weather crypto news app` • `customtkinter dashboard` • `polish information bot` • `rss news aggregator python` • `crypto weather dashboard` • `desktop information assistant` • `python auto posting tool` • `polish news aggregator`

---

## 🛠️ Built With

- Python
- CustomTkinter
- Requests
- PyAutoGUI
- Pyperclip
- Keyboard
- XML / RSS feeds
- Open-Meteo
- Binance API
- NBP API
- NASA RSS
- Hacker News API
- USGS
- Wikipedia API

---

## ⚠️ Responsible Use

InfoPulse PL automates text entry into the currently focused application. Use automation only where it is allowed and avoid flooding chats, services or communities with unwanted messages. External APIs and RSS feeds may change or become temporarily unavailable.

---

## 👨‍💻 Author

Developed by **Swir** — [@Swir](https://github.com/Swir)

---

<div align="center">

### 📡 One dashboard. Many information streams.

**Collect • Combine • Share**

⭐ Star the repository if you find it useful!

</div>
