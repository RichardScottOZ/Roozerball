# Using Godot to Run Roozerball

This guide walks you through everything you need to know about running the Roozerball 3D front-end inside the **Godot Engine** — from installing Godot for the first time, pulling the latest code from GitHub, to watching your first match in the 3D arena.

---

## What is Godot?

[Godot](https://godotengine.org/) is a free, open-source game engine. It has two parts that you will interact with:

| Part | What it is | What you use it for |
|---|---|---|
| **Godot Editor** | The IDE / development environment | Opening the project, browsing scenes and scripts, and pressing **Run** |
| **Godot Engine** (runtime) | The execution environment embedded in the editor | Runs the 3D scene while you play the game |

You do **not** need to know GDScript or 3D game development to run Roozerball. The editor is just the launcher. Once you press **Run** you are watching/playing the game.

---

## Prerequisites

Before you begin, install the following on your machine:

| Requirement | Version | Download |
|---|---|---|
| **Godot Engine** | 4.3 or later | https://godotengine.org/download/ |
| **Python** | 3.9 or later | https://www.python.org/downloads/ |
| **Git** | any recent version | https://git-scm.com/downloads |

> **Windows users:** When installing Python, tick **"Add Python to PATH"** during setup. This ensures Godot can find it.

> **macOS / Linux users:** Python is usually pre-installed. Run `python3 --version` in a terminal to confirm.

---

## Step 1 — Install Godot

1. Go to https://godotengine.org/download/
2. Download the **Standard** build for your operating system (Windows, macOS, or Linux).
   - Godot ships as a single executable — there is nothing to install. Just unzip and place it somewhere convenient (e.g. `C:\Tools\Godot\` on Windows, `/Applications/` on macOS).
3. On **macOS**, right-click the `.app` and choose **Open** the first time (required to bypass Gatekeeper).
4. On **Linux**, mark the binary executable: `chmod +x Godot_v4.x-stable_linux.x86_64`

Launching Godot for the first time opens the **Project Manager** — a window that lists projects. This is where you will import the Roozerball project.

---

## Step 2 — Get the Repository

### First-time clone

Open a terminal (Command Prompt / PowerShell on Windows, Terminal on macOS/Linux) and run:

```bash
git clone https://github.com/RichardScottOZ/Roozerball.git
cd Roozerball
```

This downloads the full repository to a local `Roozerball/` folder.

### Install Python dependencies

The Godot front-end communicates with a Python game engine in the background. Install the required Python packages:

```bash
# Create a virtual environment (recommended)
python -m venv .venv

# Activate it
# macOS / Linux:
source .venv/bin/activate
# Windows (Command Prompt):
.venv\Scripts\activate.bat
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install pygame
```

> **Note:** Pygame is only needed if you also want to use the Pygame GUI tiers. The Godot front-end itself has no extra Python dependencies beyond the standard library.

---

## Step 3 — Pull Updates and Fixes from GitHub

Whenever new features or bug fixes are pushed to the repository, update your local copy:

```bash
# Make sure you are in the Roozerball directory
cd Roozerball

# Pull the latest changes from GitHub
git pull origin main
```

If you are on a different branch (e.g. a feature branch), replace `main` with the branch name:

```bash
git pull origin <branch-name>
```

After pulling, re-activate your virtual environment and re-run `pip install pygame` if new Python packages were added.

> **Tip:** Check the repository's [commit history](https://github.com/RichardScottOZ/Roozerball/commits/main) or `CHANGELOG` for a summary of recent changes before pulling.

---

## Step 4 — Open the Godot Project

1. Launch the Godot executable. The **Project Manager** opens.
2. Click **Import**.

   ![Godot Project Manager — Import button is in the top-right area]

3. In the file browser that appears, navigate to the `Roozerball/godot/` folder you cloned.
4. Select the file `project.godot` and click **Open** (or **Import & Edit**).

   The project will appear in your project list as **Roozerball**.

5. Double-click **Roozerball** in the project list (or click **Edit**) to open it in the editor.

---

## Step 5 — A Quick Tour of the Godot Editor

When the project opens you will see several panels:

```
┌─────────────────────────────────────────────────────────────────┐
│  Menu bar   (Scene / Project / Debug / Editor / Help)           │
│  Toolbar    [▶ Run] [Stop] [Scene selector] …                   │
├──────────────┬──────────────────────────────┬───────────────────┤
│              │                              │                   │
│  Scene tree  │       3D Viewport            │  Inspector        │
│  (left)      │       (centre)               │  (right)          │
│              │                              │                   │
├──────────────┴──────────────────────────────┴───────────────────┤
│  FileSystem / Console / Debugger  (bottom tabs)                 │
└─────────────────────────────────────────────────────────────────┘
```

| Panel | Purpose |
|---|---|
| **Scene tree** (left) | Lists all nodes in the currently open scene. You normally don't need to touch this. |
| **3D Viewport** (centre) | Shows the 3D arena. Not interactive until you press Run. |
| **Inspector** (right) | Properties of the selected node. Only relevant if you are editing the project. |
| **FileSystem** (bottom-left tab) | Browse project files (`scenes/`, `scripts/`). |
| **Debugger / Console** (bottom tabs) | Shows `print()` output and error messages. Useful for troubleshooting. |

You don't need to learn any of this deeply to run the game. The one button you need is **▶ Run** (keyboard shortcut **F5**).

---

## Step 6 — Configure Python Path (if needed)

The Godot scene automatically launches the Python bridge (`roozerball/godot_bridge.py`) when it starts. It uses the command `python` by default.

**If Godot cannot find Python**, you can override the Python path via a command-line argument when launching Godot from a terminal:

```bash
# macOS / Linux
/path/to/Godot_v4.x --path /path/to/Roozerball/godot -- --python=python3

# Windows (Command Prompt)
"C:\Tools\Godot\Godot_v4.x.exe" --path "C:\path\to\Roozerball\godot" -- --python=python
```

Alternatively, the simplest fix is to ensure that `python` (or `python3`) is on your system `PATH` before launching Godot.

**To verify Python is on your PATH:**

```bash
# macOS / Linux
which python3

# Windows
where python
```

If this prints a path, Godot will find it automatically.

---

## Step 7 — Run the Game

1. With the project open in the editor, press **F5** (or click the **▶** button in the toolbar).
2. Godot compiles the project (fast — a few seconds the first time) and opens a new window titled **Roozerball**.
3. In the background, Godot automatically launches the Python bridge process. You will see startup messages in the **Debugger / Console** panel at the bottom of the editor:

   ```
   Engine ready — requesting initial board state
   ```

4. The 3D arena loads: a circular banked track with 12 sectors (A–L), stadium floodlights, spectator stands, and the central cannon. The HUD (heads-up display) shows the scoreboard and turn information at the top and bottom of the screen.

> If you see an error like `Failed to start Python bridge process`, see the [Troubleshooting](#troubleshooting) section below.

---

## Step 8 — Playing / Watching the Game

The game starts automatically with a **Computer vs Computer** match. You control the pace of play with keyboard shortcuts.

### Keyboard Controls

| Key | Action |
|---|---|
| **Space** | Advance one phase (Clock → Ball → Initiative → Movement → Combat → Scoring) |
| **T** | Play a full turn (runs all 6 phases at once) |
| **A** | Toggle auto-play mode (advances phases automatically every ~0.6 seconds) |
| **1** | Switch to overhead camera (bird's-eye view of the whole track) |
| **2** | Switch to trackside camera (orbits the arena, follows the ball) |
| **3** | Switch to goal-cam (view from behind the home goal) |

### The HUD

The on-screen HUD provides all game information:

| Element | Location | Shows |
|---|---|---|
| **Scoreboard** | Top centre | Home and Visitor team names and scores |
| **Phase indicator** | Top right | Current turn number and phase name |
| **Scrolling game log** | Bottom panel | Narrative of events this turn (tackles, goals, injuries, etc.) |
| **Penalty box display** | Side panel | Which figures are currently penalised and for how long |

### What you will see

- **Figures** (player tokens) move around the circular track each turn.
  - Capsule shapes = skaters and catchers.
  - Box shapes = motorcyclists.
  - Home team figures are one colour; visitor team another.
- **The ball** is a glowing steel sphere. It glows hotter (brighter/more orange) as temperature increases from collisions.
- **Goals** flash the screen yellow when scored.
- **Camera 2** (trackside) auto-orbits and locks on to the ball's sector for the best view of the action.

### Auto-play mode

Press **A** to toggle auto-play. Phases advance every 0.6 seconds without any input from you. Press **A** again to pause. This is the easiest way to watch a full match hands-free.

---

## Step 9 — Starting a New Match

The current implementation starts a new Computer vs Computer match automatically on launch. To restart:

1. Press **F5** to stop the running game (or close the game window).
2. Press **F5** again to start a fresh match.

---

## Project Structure Reference

For contributors or the curious, here is what the relevant files are:

```
Roozerball/
├── godot/                      ← Godot project root
│   ├── project.godot           ← Project configuration (open this in Godot)
│   ├── scenes/
│   │   └── main.tscn           ← Main 3D scene
│   └── scripts/
│       ├── game_bridge.gd      ← Autoloaded singleton; launches Python and communicates via JSON
│       ├── game_controller.gd  ← Wires arena, figures, ball, camera and HUD together
│       ├── arena_builder.gd    ← Procedurally generates the circular banked track
│       ├── figure_manager.gd   ← Creates and moves 3D figure meshes
│       ├── ball_visual.gd      ← Renders the glowing steel ball
│       ├── camera_rig.gd       ← Multi-camera system (overhead / trackside / goal-cam)
│       ├── hud.gd              ← Scoreboard, phase indicator, game log
│       └── stadium_atmosphere.gd ← Crowd silhouettes, sector labels, dust particles
└── roozerball/
    ├── godot_bridge.py         ← Python-side bridge; runs as a subprocess
    └── engine/                 ← Full Roozerball rules engine (Python)
```

### How the bridge works

```
Godot editor (F5)
    └─► Godot runtime loads main.tscn
            └─► game_bridge.gd (autoload) starts Python subprocess
                    └─► roozerball/godot_bridge.py starts
                            └─► writes initial game state to a temp JSON file
                ◄── Godot reads that file, renders the arena
                                    ┌─────────────────────────┐
    User presses Space ────────────►│ Godot writes cmd JSON   │
                                    │ Python reads it         │
                                    │ Engine runs one phase   │
                                    │ Python writes state JSON│
                                    │ Godot reads state JSON  │
                                    │ Arena/HUD update        │
                                    └─────────────────────────┘
```

No network sockets are used. Communication is entirely through two temporary JSON files in the OS user-data directory.

---

## Troubleshooting

### "Failed to start Python bridge process"

Godot cannot find the `python` executable.

**Fix:**
1. Confirm Python is installed: open a terminal and run `python --version` or `python3 --version`.
2. Make sure the command Godot uses (`python`) matches what is available. On many systems `python3` is the correct command.
3. Edit `godot/scripts/game_bridge.gd` line 17 and change:
   ```gdscript
   var python_path: String = "python"
   ```
   to:
   ```gdscript
   var python_path: String = "python3"
   ```
4. Save the file and press F5 again.

### "Timeout waiting for engine response"

The Python bridge started but stopped responding.

**Fix:**
1. Check the **Debugger / Console** tab at the bottom of the editor for Python error messages.
2. Ensure you ran `pip install pygame` inside your virtual environment (even for the Godot front-end, the engine imports some shared modules).
3. Confirm you are running from the correct directory — the repository root must contain the `roozerball/` Python package.

### Godot says the project is "too old" or "incompatible"

This project requires **Godot 4.3 or later**.

**Fix:** Download the latest stable release from https://godotengine.org/download/ and re-open the project.

### Black screen / nothing renders

**Fix:**
1. Ensure your graphics drivers are up to date.
2. The project uses the **Forward+** renderer. On very old GPUs you may need to change this: in the Godot editor go to **Project → Project Settings → Rendering → Renderer** and try **Compatibility** mode.

### The game window opens but closes immediately

**Fix:** Look at the Output/Console panel in the editor. A Python traceback there usually explains the issue. The most common cause is a missing Python module — re-run `pip install pygame` in your virtual environment.

### macOS: "Godot can't be opened because Apple cannot check it for malicious software"

**Fix:** Right-click the Godot app and choose **Open**, then confirm. You only need to do this once.

---

## Summary Checklist

- [ ] Godot 4.3+ installed
- [ ] Python 3.9+ installed and on PATH
- [ ] Repository cloned with `git clone`
- [ ] Python virtual environment created and activated
- [ ] `pip install pygame` run inside the virtual environment
- [ ] `godot/project.godot` imported in the Godot Project Manager
- [ ] Game launched with **F5**
- [ ] Python bridge started (check console for "Engine ready")
- [ ] Press **A** to enable auto-play and watch the match

---

## Further Reading

- [Roozerball Rules](Roozerball-rules.pdf) — the official rulebook
- [League Teams](league_teams.md) — pre-built team rosters
- [Rules Implementation Checklist](../roozerball-rules-to-implement.md) — full list of implemented rules
- [Godot Engine documentation](https://docs.godotengine.org/en/stable/) — if you want to explore or modify the 3D scenes
