import os

TOP_LEVEL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .utils import setup_logger