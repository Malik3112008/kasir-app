import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app

app.static_folder = os.path.join(project_root, 'static')
app.static_url_path = '/static'
