import os
from dotenv import load_dotenv

class Settings:
    """
    Simple settings wrapper that supports attribute access.
    Reads from st.secrets (Streamlit Cloud) or .env (local development).
    """
    def __init__(self):
        # Try loading from st.secrets first (Streamlit Cloud + local .streamlit/secrets.toml)
        try:
            import streamlit as st
            self._data = dict(st.secrets)
        except Exception:
            self._data = {}

        # Fallback: load .env and merge any missing keys from environment
        load_dotenv()
        for key in os.environ:
            if key not in self._data:
                self._data[key] = os.environ[key]

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"Setting '{name}' not found")

def get_settings():
    return Settings()
