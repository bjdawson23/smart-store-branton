"""
Logger Setup Script
File: utils/logger.py

This script provides logging functions for the project. Logging is an essential way to
track events and issues during software execution. This logger setup uses Python's built-in
logging module to log messages and errors both to the console and a log file.

Features:
- Logs information, warnings, and errors to the console and a log file.
- Configurable logging format and level.
"""

# Imports from Python Standard Library
import logging
import pathlib
import sys

# Add project root to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Configure logger
LOG_FOLDER = pathlib.Path("logs")
LOG_FILE = LOG_FOLDER / "project_log.log"

# Ensure the log folder exists
LOG_FOLDER.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("smart-store")


def log_example() -> None:
    """Example logging function to demonstrate logging behavior."""
    try:
        logger.info("This is an example info message.")
        logger.warning("This is an example warning message.")
        logger.error("This is an example error message.")
    except Exception as e:
        logger.error(f"An error occurred during logging: {e}")


def main() -> None:
    """Main function to execute the logger setup and demonstrate its usage."""
    logger.info("STARTING logger.py")
    
    # Call the example logging function
    log_example()
    
    logger.info("EXITING logger.py.")


# Conditional execution block that calls main() only when this file is executed directly
if __name__ == "__main__":
    main()