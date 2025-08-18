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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with _log_file_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {text}\n")


def log_tool_call(tool_name: str, agent_name: str, args: dict = None, result: str = None) -> None:
    """
    Logs tool execution details.
    Args:
        tool_name (str): Name of the tool being called
        agent_name (str): Name of the agent calling the tool
        args (dict, optional): Arguments passed to the tool
        result (str, optional): Result returned by the tool
    """
    log_text(f"TOOL_CALL: {agent_name} -> {tool_name}")
    if args:
        log_text(f"  Arguments: {args}")
    if result:
        result_preview = result[:100].replace('\n', ' ') + ('...' if len(result) > 100 else '')
        log_text(f"  Result Preview: {result_preview}")
        log_text(f"  Result Length: {len(result)} characters")


def log_agent_interaction(from_agent: str, to_agent: str = None, message_type: str = "message", content: str = "") -> None:
    """
    Logs interactions between agents.
    Args:
        from_agent (str): Source agent name
        to_agent (str, optional): Target agent name
        message_type (str): Type of interaction (message, request, response, etc.)
        content (str): Content of the interaction
    """
    if to_agent:
        log_text(f"AGENT_INTERACTION: {from_agent} -> {to_agent} [{message_type}]")
    else:
        log_text(f"AGENT_INTERACTION: {from_agent} [{message_type}]")
    
    if content:
        content_preview = content[:200].replace('\n', ' ') + ('...' if len(content) > 200 else '')
        log_text(f"  Content: {content_preview}")

def list_enums(enum_class):
    """
    Returns a list of enum names and descriptions.
    Args:
        enum_class (Enum): The enum class to list.
    Returns:
        string: comma seporated of tuples containing enum name and description.
    """
    return f"{', '.join([f'{opt.name}: {opt.description}\r\n' for opt in enum_class])}"