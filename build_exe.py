"""
Build script cho TomSamAutobot
Tạo file .exe standalone với PyInstaller
"""
import os
import sys
import subprocess
import shutil

# ========== CONFIG ==========
APP_NAME = "TomSamAutobot"
VERSION = "1.0.0"
ICON_PATH = "resources/tomsamautobot.ico"

# ===== PYINSTALLER COMMAND (UPDATED) =====
PYINSTALLER_CMD = [
    "pyinstaller",
    "--name", APP_NAME,
    "--onefile",  # Single exe file
    "--windowed",  # No console window
    "--icon", ICON_PATH,  # App icon
    
    # ===== ADD DATA FILES (FIX: Thêm cả folder resources) =====
    "--add-data", f"config.py{os.pathsep}.",
    "--add-data", f"constants.py{os.pathsep}.",
    "--add-data", f"resources{os.pathsep}resources",  # ← FIX: Add cả folder
    # ==========================================================
    
    # Hidden imports
    "--hidden-import", "PIL._tkinter_finder",
    "--hidden-import", "pyautogui",
    "--hidden-import", "pywinauto",
    "--hidden-import", "pynput",
    "--hidden-import", "pystray",
    
    # Build options
    "--clean",
    "--noconfirm",
    
    "main.py"  # Main script
]

# ========== FUNCTIONS ==========

def check_requirements():
    """Check if required tools are installed"""
    print("=" * 60)
    print("CHECKING REQUIREMENTS...")
    print("=" * 60)
    
    # Check PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        print("✓ PyInstaller installed")
    except:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check icon file
    if not os.path.exists(ICON_PATH):
        print(f"⚠ WARNING: Icon file not found at {ICON_PATH}")
        print("Continuing without icon...")
        # Remove icon option if file doesn't exist
        if "--icon" in PYINSTALLER_CMD:
            idx = PYINSTALLER_CMD.index("--icon")
            PYINSTALLER_CMD.pop(idx)  # Remove --icon
            PYINSTALLER_CMD.pop(idx)  # Remove path
    else:
        print(f"✓ Icon file found: {ICON_PATH}")
    
    # Check resources folder
    if not os.path.exists("resources"):
        print("⚠ WARNING: resources folder not found")
        os.makedirs("resources", exist_ok=True)
        print("✓ Created resources folder")
    else:
        print(f"✓ Resources folder exists")


def build_main_app():
    """Build main application"""
    print("=" * 60)
    print("BUILDING MAIN APP...")
    print("=" * 60)
    
    # Print command for debugging
    print("\nPyInstaller command:")
    print(" ".join(PYINSTALLER_CMD))
    print()
    
    try:
        subprocess.run(PYINSTALLER_CMD, check=True)
        print("\n✓ Main app built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)


def build_watchdog():
    """Build watchdog monitor"""
    print("=" * 60)
    print("BUILDING WATCHDOG MONITOR...")
    print("=" * 60)
    
    watchdog_cmd = [
        "pyinstaller",
        "--name", "watchdog_monitor",
        "--onefile",
        "--console",  # Keep console for watchdog
        "--clean",
        "--noconfirm",
        "watchdog_monitor.py"
    ]
    
    try:
        subprocess.run(watchdog_cmd, check=True)
        print("\n✓ Watchdog built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Watchdog build failed: {e}")
        sys.exit(1)


def organize_dist():
    """Organize dist folder"""
    print("=" * 60)
    print("ORGANIZING DIST FOLDER...")
    print("=" * 60)
    
    # Copy watchdog to main dist
    watchdog_src = f"dist/watchdog_monitor.exe"
    watchdog_dst = f"dist/{APP_NAME}/watchdog_monitor.exe"
    
    if os.path.exists(watchdog_src):
        # Create folder if needed
        os.makedirs(f"dist/{APP_NAME}", exist_ok=True)
        shutil.copy(watchdog_src, watchdog_dst)
        print(f"✓ Copied watchdog to {watchdog_dst}")
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"✓ Output folder: dist/{APP_NAME}/")
    print(f"✓ Main executable: dist/{APP_NAME}.exe")
    print(f"✓ Watchdog: dist/{APP_NAME}/watchdog_monitor.exe")
    print("=" * 60)


def clean_build_files():
    """Clean temporary build files"""
    print("=" * 60)
    print("CLEANING BUILD FILES...")
    print("=" * 60)
    
    folders_to_remove = ["build", "__pycache__"]
    files_to_remove = [f"{APP_NAME}.spec", "watchdog_monitor.spec"]
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Removed {folder}/")
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Removed {file}")


def main():
    """Main build process"""
    print("\n" + "=" * 60)
    print(f"BUILDING {APP_NAME} v{VERSION}")
    print("=" * 60 + "\n")
    
    # Steps
    check_requirements()
    build_main_app()
    build_watchdog()
    organize_dist()
    clean_build_files()
    
    print("\n" + "=" * 60)
    print("✓ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nYour application is ready in dist/{APP_NAME}.exe")
    print(f"Make sure watchdog_monitor.exe is in the same folder!")
    print()


if __name__ == "__main__":
    main()
