"""
Build script for PyInstaller.
Creates a single executable file: Commander.exe
"""

import PyInstaller.__main__
import os
from pathlib import Path

# Get project root
ROOT = Path(__file__).parent

# PyInstaller arguments
args = [
    "main.py",                          # Entry point
    "--name=Commander",                 # Output executable name
    "--onefile",                        # Single file executable
    "--console",                        # Show console for debugging (change to --windowed for release)
    # "--icon=assets/icon.ico",         # Icon (uncomment if icon exists)
    # "--add-data=assets;assets",       # Include assets folder (uncomment if needed)
    "--hidden-import=customtkinter",    # Ensure customtkinter is included
    "--hidden-import=bleak",             # Ensure bleak is included
    "--hidden-import=psutil",           # Ensure psutil is included
    "--collect-all=customtkinter",      # Collect all customtkinter data
    "--noconfirm",                      # Overwrite output without asking
    "--clean",                          # Clean cache before building
]

# Add core and ui modules
args.extend([
    "--add-data=core;core",
    "--add-data=ui;ui",
])

# Create assets directory if it doesn't exist
assets_dir = ROOT / "assets"
assets_dir.mkdir(exist_ok=True)

# Check if icon exists (commented out for now)
# icon_path = ROOT / "assets" / "icon.ico"
# if icon_path.exists():
#     args.append("--icon=assets/icon.ico")

print("Building Commander.exe...")
print(f"Arguments: {' '.join(args)}")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("\nBuild complete!")
print(f"Executable location: {ROOT / 'dist' / 'Commander.exe'}")

