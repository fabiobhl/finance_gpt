import os
import json
import logging
from logging.handlers import SMTPHandler
from finance_gpt import TOP_LEVEL_DIR


def load_credentials() -> dict:
    """Load credentials from credentials.json file."""
    
    credentials_path = os.path.join(TOP_LEVEL_DIR, "config", "credentials.json")
    try:
        with open(credentials_path) as f:
            credentials = json.load(f)    
    except Exception:
        print("Error loading credentials.json file.")
    
    return credentials
    
def load_tickers() -> list[str]:
    """Loads all tickers from the tickers.json file."""
    tickers_path = os.path.join(TOP_LEVEL_DIR, "tickers.json")
    with open(tickers_path) as f:
        tickers = json.load(f)
    
    return tickers

# logging setup

def load_logging_config() -> dict:
    """Load logging config from logging_config.json file."""
    
    logging_config_path = os.path.join(TOP_LEVEL_DIR, "config", "logging_config.json")
    try:
        with open(logging_config_path) as f:
            logging_config = json.load(f)    
            return logging_config
    except Exception as e:
        print("Error loading logging_config.json file.")
        raise e

def log_level_from_string(log_level: str) -> int:
    
    if log_level.lower() == "debug":
        return logging.DEBUG
    elif log_level.lower() == "info":
        return logging.INFO
    elif log_level.lower() == "warning":
        return logging.WARNING
    elif log_level.lower() == "error":
        return logging.ERROR
    elif log_level.lower() == "critical":
        return logging.CRITICAL
    else:
        raise ValueError(f"Unknown log level {log_level}.")

def setup_logging_folder() -> None:
    """Setup logging folder."""
    path = os.path.join(TOP_LEVEL_DIR, "logs")
    if not os.path.exists(path):
        os.mkdir(path)

def setup_logger(name: str) -> logging.Logger:
    """Setup logger."""
    # setup logging folder
    setup_logging_folder()
    
    # load logging config
    logging_config = load_logging_config()
    
    # get the log level
    log_level = log_level_from_string(logging_config["logging_level"])
    # get the file mode
    file_mode = logging_config["file_mode"]
    
    # get the logger
    logger = logging.getLogger(name)
    # set the log level
    logger.setLevel(log_level)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # create a unique file handler for this module
    path = os.path.join(TOP_LEVEL_DIR, "logs", f"{name}.log")
    file_handler_unique = logging.FileHandler(path, mode=file_mode)
    file_handler_unique.setLevel(log_level)
    file_handler_unique.setFormatter(formatter)
    
    # create a file handler for all modules
    path = os.path.join(TOP_LEVEL_DIR, "logs", "all.log")
    file_handler_all = logging.FileHandler(path, mode=file_mode)
    file_handler_all.setLevel(log_level)
    file_handler_all.setFormatter(formatter)

    logger.addHandler(file_handler_unique)
    logger.addHandler(file_handler_all)
    
    # create a email handler
    email_conf = logging_config["email_logging"]
    if email_conf["enabled"]:
        email_handler = SMTPHandler(
            mailhost=(email_conf["smtp_server"], email_conf["smtp_port"]),  # Specify the SMTP server and port
            fromaddr=email_conf["fromaddr"],    # Your Gmail address
            toaddrs=email_conf["toaddrs"],   # List of recipient email addresses
            subject=email_conf["subject"],
            credentials=(email_conf["credentials"]["username"], email_conf["credentials"]["password"]),  # Your Gmail credentials
            secure=()
        )
        email_handler.setLevel(email_conf["logging_level"])
        email_handler.setFormatter(formatter)
        
        logger.addHandler(email_handler)
    
    return logger

if __name__ == "__main__":
    credentials = load_credentials()
    print(credentials)