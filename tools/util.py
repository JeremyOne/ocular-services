import threading
from datetime import datetime

_log_file_lock = threading.Lock()
_log_file_path = None

def load_template(template_path: str = "reports/template.md") -> str:
    """
    Loads the text template file into a string variable.
    Args:
        template_path (str): Path to the text template file.
    Returns:
        str: Contents of the text template file.
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading template: {e}"


def log_text(text: str, log_file: str = None) -> None:
    """
    Logs the given text to a singleton log file.
    Args:
        text (str): The text to log.
        log_file (str, optional): Path to the log file. Defaults to singleton file.
    """
    global _log_file_path

    if _log_file_path is None:
        _log_file_path = f"reports/ocular_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"


    path = log_file if log_file else _log_file_path
    with _log_file_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")