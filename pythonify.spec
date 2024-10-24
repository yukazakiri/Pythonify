# ... (previous code remains the same)

a = Analysis(
    ['pythonify_clean.py'],
    pathex=[],
    binaries=binaries,
    datas=ytmusicapi_datas + [('.env', '.')],  # Include .env file
    hiddenimports=['dotenv'],
    # ... (rest of the configuration remains the same)
)

# ... (rest of the file remains the same)
