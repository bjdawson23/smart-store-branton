import pathlib
import sys

# Add project root to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

print(sys.path)

from utils.logger import logger
logger.info("Test log message")