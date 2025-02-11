from flask import Flask
from src.app import create_app

app = create_app()

# Vercel serverless function entry point
def handler(request, response):
    return app(request, response)