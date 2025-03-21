import os
import sys

# Get the absolute path to the src directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, project_root)
