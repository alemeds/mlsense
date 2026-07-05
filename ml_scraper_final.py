"""Entrypoint for MLSENSE v2 application.

This file is the Streamlit Cloud entrypoint and must retain its name.
All functionality is delegated to the mlsense package.
"""

if __name__ == "__main__":
    from mlsense.app import main
    main()
