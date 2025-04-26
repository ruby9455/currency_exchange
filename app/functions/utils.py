def _read_toml(file_path: str) -> dict:
    """
    Read a TOML file and return its contents as a dictionary.
    """
    import toml
    try:
        with open(file_path, 'r') as file:
            data = toml.load(file)
        return data
    except Exception as e:
        print(f"Error reading TOML file: {e}")
        return {}

