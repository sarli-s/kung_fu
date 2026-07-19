import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Kung Fu Chess")
    parser.add_argument("--gui", action="store_true", help="Run with graphical interface")
    args = parser.parse_args()
    
    if args.gui:
        # GUI mode
        from gui_mode import run_gui
        run_gui()
    else:
        # Text input mode (default)
        from run import main as run_main
        run_main()

if __name__ == "__main__":
    main()
