import os

# Centralized configuration for the application.
# Reads environment variables and provides defaults for local development.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Other configuration variables (e.g. secret keys, allowed hosts) can be added here
