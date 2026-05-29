import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app

# Ensure static files work in Vercel serverless
app.static_folder = os.path.join(project_root, 'static')
app.static_url_path = '/static'

# Vercel handler
