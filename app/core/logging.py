import logging
import logging.config
import yaml
import os

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open("log_conf.yaml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    # Create a global logger
    global logger
    logger = logging.getLogger(__name__)

# Create a global logger
logger = None

# Call setup_logging at the module level
setup_logging()