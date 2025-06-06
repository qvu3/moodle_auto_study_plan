"""
Central configuration module that loads environment variables.
This module can be used in both local development (with .env file) and in AWS Lambda.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file for local development
# In GitHub Actions, these will be set as environment variables directly
load_dotenv()

# --- Database Configuration ---
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# --- Moodle API Configuration ---
MOODLE_URL = os.getenv('MOODLE_URL')
MOODLE_TOKEN = os.getenv('MOODLE_TOKEN')

# --- Email Configuration ---
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_NAME = os.getenv('SENDER_NAME')

# --- AI API Keys ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# --- Google API Credentials ---
# In GitHub Actions, the entire JSON content is stored in a secret
GMAIL_CREDENTIALS_JSON_STR = os.getenv('GMAIL_CREDENTIALS_JSON')
GMAIL_CREDENTIALS = json.loads(GMAIL_CREDENTIALS_JSON_STR) if GMAIL_CREDENTIALS_JSON_STR else None

# Define the scopes for Google API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# --- Functions for Validation and Summarization ---

def validate_config():
    """Validates that all necessary configuration variables are set."""
    required_vars = {
        'Database': [DB_HOST, DB_USER, DB_PASSWORD, DB_NAME],
        'Moodle': [MOODLE_URL, MOODLE_TOKEN],
        'Email': [SENDER_EMAIL, SENDER_NAME],
        'AI Keys': [GEMINI_API_KEY],  # Assuming Gemini is the primary one needed
        'Google Credentials': [GMAIL_CREDENTIALS]
    }
    
    missing_config = {}
    for section, variables in required_vars.items():
        if not all(variables):
            missing_config[section] = "One or more variables are missing"
            
    return missing_config

def get_config_summary():
    """Returns a summary of the configuration for logging (with sensitive data masked)."""
    summary = {
        "DB_HOST": DB_HOST,
        "DB_USER": DB_USER,
        "DB_NAME": DB_NAME,
        "MOODLE_URL": MOODLE_URL,
        "SENDER_EMAIL": SENDER_EMAIL,
        "SENDER_NAME": SENDER_NAME,
        "DB_PASSWORD_SET": "Yes" if DB_PASSWORD else "No",
        "MOODLE_TOKEN_SET": "Yes" if MOODLE_TOKEN else "No",
        "GEMINI_API_KEY_SET": "Yes" if GEMINI_API_KEY else "No",
        "ANTHROPIC_API_KEY_SET": "Yes" if ANTHROPIC_API_KEY else "No",
        "OPENAI_API_KEY_SET": "Yes" if OPENAI_API_KEY else "No",
        "GMAIL_CREDENTIALS_SET": "Yes" if GMAIL_CREDENTIALS else "No"
    }
    return summary