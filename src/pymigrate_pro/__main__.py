import sys
from .app import PyMigrateApp

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    # Minimal CLI placeholder. Replace with click/argparse as needed.
    if not argv or argv[0] in {"-h", "--help"}:
        print("Usage: python -m pymigrate_pro")
    else:
        app = PyMigrateApp()
        app.mainloop()

if __name__ == "__main__":
    main()
