import os


"""
The home of any variable that should never change or be overwritten
"""

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # ~/ClockPy/
FILES = os.path.join(ROOT, 'files')  # ~/ClockPy/files/
