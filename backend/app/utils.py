from logging import Logger
import logging
import re

def sanitize_string(string: str):
    return re.sub(r"[\t\n\r]+", " ", string)

def get_logger() -> Logger:
    return logging.getLogger("JobHuntr")