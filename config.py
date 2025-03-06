"""
Central configuration module that loads environment variables.
This module can be used in both local development (with .env file) and in AWS Lambda.
"""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Moodle API Configuration
MOODLE_URL = os.getenv('MOODLE_URL')
MOODLE_TOKEN = os.getenv('MOODLE_TOKEN')
MOODLE_COURSE_ID = int(os.getenv('MOODLE_COURSE_ID', '0'))

# AI API Configuration
AI_API_TYPE = os.getenv('AI_API_TYPE', 'anthropic')
AI_API_KEY = os.getenv('AI_API_KEY')
AI_MAX_RETRIES = int(os.getenv('AI_MAX_RETRIES', '5'))

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', 'Your Personalized Study Plan - ')
SENDER_NAME = os.getenv('SENDER_NAME', 'Black Belt Test Prep')

def validate_config() -> Dict[str, str]:
    """
    Validate that all required configuration variables are set.
    
    Returns:
        Dictionary of missing or invalid configuration variables
    """
    missing = {}
    
    # Check Moodle configuration
    if not MOODLE_URL:
        missing['MOODLE_URL'] = 'Missing Moodle URL'
    if not MOODLE_TOKEN:
        missing['MOODLE_TOKEN'] = 'Missing Moodle API token'
    if MOODLE_COURSE_ID <= 0:
        missing['MOODLE_COURSE_ID'] = 'Invalid or missing Moodle course ID'
    
    # Check AI API configuration
    if not AI_API_KEY:
        missing['AI_API_KEY'] = 'Missing AI API key'
    if AI_API_TYPE not in ['anthropic', 'openai']:
        missing['AI_API_TYPE'] = f'Invalid AI API type: {AI_API_TYPE}'
    
    # Check email configuration
    if not SENDER_EMAIL:
        missing['SENDER_EMAIL'] = 'Missing sender email'
    if not SENDER_PASSWORD:
        missing['SENDER_PASSWORD'] = 'Missing sender password'
    
    return missing

def get_config_summary() -> str:
    """
    Get a summary of the current configuration (with sensitive data masked).
    
    Returns:
        A string summarizing the current configuration
    """
    return f"""
Configuration Summary:
---------------------
Moodle URL: {MOODLE_URL}
Moodle Course ID: {MOODLE_COURSE_ID}
AI API Type: {AI_API_TYPE}
AI API Key: {'*' * 8 + AI_API_KEY[-4:] if AI_API_KEY else 'Not set'}
SMTP Server: {SMTP_SERVER}:{SMTP_PORT}
Sender Email: {SENDER_EMAIL}
""" 