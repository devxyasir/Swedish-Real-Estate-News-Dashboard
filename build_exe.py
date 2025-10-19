"""
Build script for creating standalone executable
Run this script to build the News Dashboard executable
"""

import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("=" * 70)
    print("Building News Dashboard Executable")
    print("=" * 70)
    
    # Get the current directory
    base_dir = Path(__file__).parent
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=News Dashboard',
        '--onefile',
        '--windowed',
        '--noconsole',
        '--icon=news.png',
        '--add-data=web;web',
        '--hidden-import=eel',
        '--hidden-import=bottle',
        '--hidden-import=bottle_websocket',
        '--hidden-import=gevent',
        '--hidden-import=gevent.socket',
        '--hidden-import=geventwebsocket',
        '--hidden-import=bs4',
        '--hidden-import=lxml',
        '--hidden-import=deep_translator',
        '--hidden-import=deep_translator.google',
        '--hidden-import=tkinter',
        # All scraper modules
        '--hidden-import=fastighetsvarlden_scraper',
        '--hidden-import=cision_scraper',
        '--hidden-import=lokalguiden_scraper',
        '--hidden-import=di_scraper',
        '--hidden-import=fastighetsnytt_scraper',
        '--hidden-import=nordicpropertynews_scraper',
        # Config module
        '--hidden-import=config',
        '--collect-all=eel',
        '--noconfirm',
        'app.py'
    ]
    
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("\n" + "=" * 70)
        print("✅ Build completed successfully!")
        print("=" * 70)
        print(f"\nExecutable location: {base_dir / 'dist' / 'News Dashboard.exe'}")
        print("\nYou can now:")
        print("1. Run the executable from the 'dist' folder")
        print("2. Data will be saved to: Documents/News Dashboard Data/")
        print("3. Share the executable with others - it's fully portable!")
        print("\n" + "=" * 70)
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print("❌ Build failed!")
        print("=" * 70)
        print(f"\nError: {e}")
        print("\nPlease make sure:")
        print("1. PyInstaller is installed: pip install pyinstaller")
        print("2. All dependencies are installed: pip install -r requirements.txt")
        print("3. You're running this from the project root directory")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

