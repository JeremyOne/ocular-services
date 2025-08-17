import threading
from datetime import datetime
import os

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

    # Ensure the reports directory exists
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
    global _log_file_path

    if _log_file_path is None:
        _log_file_path = f"reports/ocular_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"


    path = log_file if log_file else _log_file_path
    with _log_file_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

def list_enums(enum_class):
    """
    Returns a list of enum names and descriptions.
    Args:
        enum_class (Enum): The enum class to list.
    Returns:
        string: comma seporated of tuples containing enum name and description.
    """
    return f"{', '.join([f'{opt.name}: {opt.description}\r\n' for opt in enum_class])}"