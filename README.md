#PARAS MANOHAR AREKAR 
#AD2331 SY C DIGITAL MARKETING
# 🌍 EcoProtect — 1:1 Planetary Observation Center & Global Crisis Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![WebGL Three.js](https://img.shields.io/badge/Graphics-Three.js%20%7C%20Globe.gl-000000?style=flat&logo=three.js&logoColor=white)](https://globe.gl/)
[![C++17](https://img.shields.io/badge/Engine-C%2B%2B17-00599C?style=flat&logo=c%2B%2B&logoColor=white)](https://isocpp.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **EcoProtect** is a real-time, interactive planetary crisis observation and environmental awareness platform. It pairs high-performance WebGL 3D geospatial visualization with scientific carbon modeling, community engagement, and crisis ledgers.

---

## 🌟 Key Features

### 🌐 3D Planetary Crisis Observation Center
- **Zero-Latency Procedural Earth**: Rendered in WebGL with glowing cyan coastlines, continental landmasses, emerald Prime Meridian, and coordinate graticules without reliance on external image downloads.
- **4,800+ Planetary Disasters Visualized**: Complete catalog of historical and ongoing natural and anthropogenic catastrophes.
- **Up to 999 3D Map Pointer Pins**: Modeled with custom Google Maps pointer geometry (tapered needle touching the crust + bulbous sphere head + white center eye) directly on the rotating sphere.
- **4,864 Glowing 3D Beacon Columns**: GPU-instanced and merged for silky-smooth 60 FPS performance.
- **Ground-Zero Radar Pulse Rings**: Animated sonic waves marking high-impact catastrophic centers.
- **Instant Planetary Crisis Ledger & HUD**: Live global metrics stream (Fatalities, Economic Damages, Land Area Destroyed, CO₂ PPM) with search, severity filter chips, and timeline navigation.

### 🍃 Comprehensive Environmental Suites
- **Global Carbon & Environmental Calculators**: Multi-sector impact assessment (transportation, electricity, heating, dietary choices) backed by high-precision C++ calculation logic.
- **Interactive Domains**:
  - 🌲 **Forests & Deforestation Tracker**: Reforestation initiatives and canopy degradation analysis.
  - ⚡ **Renewable Energy & Grid Transition**: Solar, wind, hydro, and geothermal modeling.
  - 💧 **Water Conservation & Freshwater Depletion**: Aquifer stress metrics and oceanic plastic maps.
  - ♻️ **Circular Economy & Waste Reduction**: Zero-waste audits and recycling analytics.
  - 🐝 **Biodiversity Loss & Endangered Species**: Ecosystem preservation index.
  - 📰 **Live Ecological Newsfeed & Intelligence**: Curated environmental stories and scientific briefs.

### 🛡️ Enterprise-Grade Authentication & Community
- **OTP Verification & Authentication**: One-time-passcode email/sms simulation for secure user onboarding and sign-in.
- **User Action Pledges**: Track personalized climate commitments and measure community-wide collective CO₂ reduction.
- **Administrator Governance Dashboard**: Real-time management of reported events, user accounts, and ecological alert bulletins.

---

## 🛠️ Architecture & Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla JavaScript, Modern CSS3 Glassmorphism, Three.js, Globe.gl |
| **Backend** | Python Flask, Jinja2 Templating, REST API |
| **Database** | SQLite3 (`ecoplanet.db`) with automatic schema bootstrapping |
| **Scientific Engine** | High-precision C++17 Engine (`eco_engine.cpp`) with automated fallback |
| **Datasets** | Compact, core, and detail JSON feeds for 4,800+ disaster records |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9 or higher
- (Optional) GCC/Clang/MSVC compiler if compiling the native C++ engine

### 1. Clone the Repository
```bash
git clone https://github.com/PARASAREKAR/EcoProtect.git
cd EcoProtect
```

### 2. Install Dependencies
```bash
pip install flask
```

### 3. (Optional) Build Native C++ Engine
```cmd
build_cpp.bat
```
*(If a C++ compiler is not present, the Flask backend automatically uses its embedded high-precision Python math fallback engine seamlessly.)*

### 4. Launch the Platform
```cmd
start.bat
```
*Or directly via Python:*
```bash
python app.py
```

### 5. Access the Web Interface
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```
- **Interactive 3D Globe**: `http://127.0.0.1:5000/globe`
- **Default Admin Account**: `admin` / `admin123`

---

## 📂 Project Structure

```
EcoProtect/
├── app.py                         # Core Flask application, routing, and REST APIs
├── database.py                    # SQLite database schema, user auth & OTP logic
├── eco_engine.cpp                 # High-performance C++ scientific carbon computation engine
├── build_cpp.bat                  # Compiler script for C++ engine
├── start.bat                      # One-click Windows launch script
├── hazards_data.py                # Crisis intelligence catalog & data loaders
├── generate_massive_hazards.py    # Catalog generator for 4,800+ disaster entries
├── static/
│   ├── css/                       # Glassmorphism, dark-mode, and component stylesheets
│   ├── data/                      # 4,800+ hazards datasets (core, details, compact, master)
│   ├── js/                        # Three.js, Globe.gl, calculators, and API client scripts
│   └── textures/                  # Geosphere assets and environmental maps
├── templates/                     # Jinja2 HTML views (globe, index, calculators, auth, etc.)
└── README.md                      # Platform documentation
```

---

## 📜 License
This project is open-source and licensed under the [MIT License](LICENSE).
