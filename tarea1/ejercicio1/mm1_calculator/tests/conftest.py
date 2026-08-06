import os
import sys


HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(HERE)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
