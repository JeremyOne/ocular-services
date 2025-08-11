from datetime import datetime
from . import util

def get_current_datetime() -> str:
    """
    Returns the current date and time in ISO format.
    """
    util.log_text("get_current_datetime called")
    return datetime.now().isoformat()