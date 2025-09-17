# Nine Men’s Morris – Python Implementation  

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)  
![License](https://img.shields.io/badge/License-MIT-green)  
![UI](https://img.shields.io/badge/UI-Console%20%7C%20GUI-orange)  
![AI](https://img.shields.io/badge/AI-Minimax%20with%20Alpha--Beta-purple)  

A complete Python implementation of the classic board game **Nine Men’s Morris**, showcasing **Object-Oriented Programming (OOP) principles**, a **layered software architecture**, and an **optimized Minimax algorithm** for AI decision-making.


---

<img src="https://i.imgur.com/LZ1706f.png" alt="Game Screenshot" width="400"/>


## ✨ Features
- 🎮 **Two UI modes**: GUI (with animations and sound) or console based.
- 🕹️ **Player vs Player** or **Player vs AI** gameplay.
- 🧠 **AI opponent** powered by Minimax + alpha–beta pruning.  
- 👥 **Player management**: add, remove, and manage player profiles, stored using **binary files (`.pkl`)**.  
- 🏛️ **Layered architecture** with clear separation of concerns.  
- 🎨 **Board and piece art**, smooth animations.  
- 🔊 **Sound effects** for moves, captures, and game events.
- 🧩 **Bitmap representaion** for efficient game state management.
- 📚 **Well-documented source code** with full HTML docs in `docs/`.  


---


## 🧠 The Minimax Algorithm
- **Bitmap representation**: the board state is stored compactly as a bitmap, allowing efficient evaluation and move generation.  
- **Recursive decision-making**: simulates future moves for both players.  
- **Alpha–beta pruning**: drastically reduces the number of nodes explored.  
- **Heuristic evaluation**: considers number of mills, piece count, mobility, and threats.  

This creates a performant AI that may prove quite the challenge.


---


## ⚙️ Configuration
The file `settings.properties` controls how the game runs.  

### Example:
```properties
# Use GUI = True to start the game with a graphical user interface
GUI = True
```


---


## 📦 Installation & Dependencies
Install dependencies with:
```bash
pip install -r requirements.txt
```


**Requirements:**
- `playsound` – for sound playback.
- `tkinter` – standard library (may require `python3-tk` on Linux).


---


## 📖 Documentation
- **HTML documentation** available in `docs/`.
- Source code is fully commented with docstrings and explanations.


---


## 🚀 Running the Game
1. Clone the repo:
```bash
git clone https://github.com/XZE3N/NineMensMorris.git
cd NineMensMorris
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Adjust `settings.properties` (choose UI).
4. Run the game:
```bash
python main.py
```


---


## 👥 Player Management
- Add, remove, and manage players from within the game.
- Player data is stored as **binary files (`.pkl`)** in the `data/` folder.
- This allows persistent profiles across sessions.


---


## 🧪 Testing
Run tests with:
```bash
pytest tests.py
```


---


## 🎨 Visuals & Audio
- Custom **board and piece artwork**.
- **Animations** highlight moves, captures, and mills.
- **Sound effects** for immersive feedback.

<img src="https://i.imgur.com/zAYfRF2.png" alt="Game Screenshot" width="400"/> 
<img src="https://i.imgur.com/hrVBDRD.png" alt="Game Screenshot" width="400"/>

---


## 📂 Project Structure

```
/root
|
├── domain/             # Core entities (Board, Player, Color) – bitmap-based state
├── repository/         # Player repository (binary storage using pickle)
├── services/           # Game logic, AI (Minimax), player services
├── validation/         # Validators for moves and states
├── ui/                 # Console and GUI frontends
├── exceptions/         # Custom error handling
├── config/             # Configuration utils
├── audio/              # Sound assets
├── ico/                # Icons and artwork
├── data/               # Binary player storage and misc data
├── docs/               # HTML documentation
├── main.py             # Entry point
├── settings.properties # Config file (UI, AI depth, sound, etc.)
└── tests.py            # Unit tests
```


---


## 📜 License
This project is distributed under the **MIT License**.
