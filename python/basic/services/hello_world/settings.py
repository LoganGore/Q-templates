import os
from dotenv import load_dotenv
import logging
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(verbose=True, dotenv_path=os.path.join(PROJECT_ROOT, '.env'))

#0.0.0.0 binds to all available
SERVICE_ADDRESS = '0.0.0.0'
SERVICE_PORT = os.getenv('SERVICE_PORT')

LOG_LEVEL = logging.WARN
