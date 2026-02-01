"""
Script to run the backend with environment variables
"""

import os
import sys
import dotenv

# Set UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables from .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Check if Hugging Face token is configured
if not os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HUGGINGFACE_TOKEN') == '':
    print("Warning: Hugging Face token not configured!")
    print()
    print("To use the chatbot, you need to:")
    print("1. Go to https://huggingface.co/settings/tokens")
    print("2. Create a new token with 'write' permissions")
    print("3. Copy the token and paste it into backend/.env file")
    print()
    print("Current .env file content:")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'backend', '.env'), 'r') as f:
            print(f.read())
    except:
        print("File not found")
    print()
    print("For testing purposes, you can run the health check and question analysis endpoints.")
    print("The chat endpoint will fail without a valid token.")
    print()

# Run the backend
os.chdir(os.path.dirname(__file__))
os.system("cd backend && python main.py")