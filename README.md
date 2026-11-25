# \# Gesture-Control

# 

# Controlling the TV remote is a small thing — until it isn't.

# 

# For people with limited mobility, arthritis, or age-related motor difficulties,

# reaching for a remote, finding the right button, and pressing it accurately is

# a real daily friction. Gesture-Control removes that entirely. Point a camera at

# the room, and your hand becomes the remote.

# 

# Built with Python and MediaPipe, this runs on a laptop or Raspberry Pi and

# controls system audio or a smart TV over WiFi — no hardware modifications,

# no special equipment, no app to install.

# 

# \---

# 

# \## Gestures

# 

# | Gesture | Action |

# |---|---|

# | ✌️ Peace sign (index + middle fingers up) | Play / Pause |

# | ✊ Fist (all fingers curled, hold 0.5s) | Mute / Unmute |

# | 🤏 Pinch (thumb + index, hold 5s) | Adjust volume — move hand up/down |

# 

# The 5-second pinch entry delay prevents accidental volume changes during

# normal hand movement.

# 

# \---

# 

# \## Requirements

# 

# ```

# Python 3.9+

# mediapipe

# opencv-python

# pycaw

# comtypes

# pystray

# Pillow

# ```

# 

# Install dependencies:

# 

# ```bash

# pip install -r requirements.txt

# ```

# 

# \---

# 

# \## Setup

# 

# \*\*1. Clone the repo\*\*

# ```bash

# git clone https://github.com/Sivavenator/Gesture-control.git

# cd Gesture-control

# ```

# 

# \*\*2. Create a virtual environment\*\*

# ```bash

# python -m venv venv

# venv\\Scripts\\activate      # Windows

# source venv/bin/activate   # Linux / Raspberry Pi

# ```

# 

# \*\*3. Install dependencies\*\*

# ```bash

# pip install -r requirements.txt

# ```

# 

# \*\*4. Run\*\*

# ```bash

# python main.py

# ```

# 

# A system tray icon appears when running. Right-click to quit.

# 

# \---

# 

# \## Run on Windows Startup (optional)

# 

# Create a `.bat` file in your Windows startup folder

# (`shell:startup` in the Run dialog):

# 

# ```bat

# @echo off

# cd /d "C:\\path\\to\\Gesture-control"

# "venv\\Scripts\\pythonw.exe" main.py

# ```

# 

# \---

# 

# \## Project Structure

# 

# ```

# Gesture-control/

# ├── main.py               # Main loop, gesture state machine

# ├── gesture\_detector.py   # MediaPipe hand landmark logic

# ├── tv\_controller.py      # Audio / TV control interface

# ├── config.py             # Tuning constants

# └── requirements.txt

# ```

# 

# \---

# 

# \## Smart TV Control via Raspberry Pi

# 

# The laptop prototype controls system audio on Windows. The next version runs

# entirely on a \*\*Raspberry Pi 5\*\*, mounted near the TV, controlling it directly

# over WiFi — no laptop needed, no HDMI cable, no remote.

# 

# \### How it works

# 

# The Pi sits on the same home WiFi network as the LG TV. A USB webcam or

# CSI camera watches the room. When a gesture is detected, the Pi sends a

# command to the TV using the \*\*LG webOS API\*\* over a local network connection —

# the same protocol the official LG ThinQ app uses.

# 

# ```

# \[Camera] → \[Raspberry Pi 5] → \[WiFi LAN] → \[LG TV webOS API]

# ```

# 

# No internet required. Everything runs locally on the home network.

# 

# \### Why a Raspberry Pi

# 

# A laptop cannot sit permanently by the TV. The Pi draws under 5W at idle,

# runs headlessly with no screen, and boots straight into the gesture control

# service on power-up via systemd. It is always on, always ready.

# 

# \### TV Control Features (Phase 2)

# 

# | Gesture | Action |

# |---|---|

# | ✌️ Peace sign | Play / Pause |

# | ✊ Fist | Mute / Unmute |

# | 🤏 Pinch + move | Volume up / down |

# 

# Commands are sent via \[pywebostv](https://github.com/supersaiyansubtlety/pywebostv),

# a Python library for the LG webOS API. On first run, the TV displays a

# pairing prompt — accept once, and credentials are saved locally. All

# subsequent connections are automatic.

# 

# \### Hardware Required

# 

# | Component | Notes |

# |---|---|

# | Raspberry Pi 5 8GB | 8GB recommended for CV workload headroom |

# | Official 27W USB-C power supply | Pi 5 requires 5V/5A — standard phone chargers may throttle |

# | 64GB microSD (A2 rated) | Faster random read/write for OS |

# | Active cooler | MediaPipe runs the CPU hard — passive cooling is not enough |

# | USB webcam (UVC) | Plug and play on Pi OS, no driver needed |

# | LG Smart TV with webOS | Must be on the same WiFi subnet as the Pi |

# 

# \### Setup on Raspberry Pi

# 

# \*\*1. Flash Pi OS Lite 64-bit\*\* (no desktop needed — headless)

# 

# \*\*2. Enable SSH and set WiFi\*\* in Raspberry Pi Imager before flashing

# 

# \*\*3. Transfer the project\*\*

# ```bash

# scp -r ./Gesture-control pi@raspberrypi.local:\~/

# ```

# 

# \*\*4. Install dependencies\*\*

# ```bash

# pip install mediapipe opencv-python pywebostv pystray Pillow --break-system-packages

# ```

# 

# \*\*5. Find your TV's IP address\*\*

# 

# On the LG TV: Settings → Network → Wi-Fi Connection → Advanced Wi-Fi → IP Address

# 

# \*\*6. Run once to pair\*\*

# ```bash

# python main.py

# ```

# Accept the pairing prompt on the TV screen. Credentials save to

# `tv\_credentials.json` automatically.

# 

# \*\*7. Set up autostart with systemd\*\*

# 

# Create `/etc/systemd/system/gesture-control.service`:

# 

# ```ini

# \[Unit]

# Description=Gesture Control

# After=network.target

# 

# \[Service]

# ExecStart=/usr/bin/python3 /home/pi/Gesture-control/main.py

# WorkingDirectory=/home/pi/Gesture-control

# Restart=always

# User=pi

# 

# \[Install]

# WantedBy=multi-user.target

# ```

# 

# Enable it:

# ```bash

# sudo systemctl enable gesture-control

# sudo systemctl start gesture-control

# ```

# 

# The service starts automatically on every boot.

# 

# \---

# 

# \## Who This Is For

# 

# Primarily built for:

# \- Elderly users who find small remote buttons difficult to operate

# \- People with arthritis, tremors, or limited hand dexterity

# \- Anyone with a mobility condition affecting fine motor control

# 

# The gesture set is intentionally simple — large, deliberate movements

# that are easy to make even with reduced dexterity.

# 

# \---

# 

# \## Tech Stack

# 

# \- \[MediaPipe](https://mediapipe.dev/) — hand landmark detection

# \- \[OpenCV](https://opencv.org/) — camera feed

# \- \[pycaw](https://github.com/AndreyMZ/pycaw) — Windows audio control

# \- \[pywebostv](https://github.com/supersaiyansubtlety/pywebostv) — LG webOS TV control (Phase 2)

