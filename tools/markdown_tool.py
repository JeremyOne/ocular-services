import os
import time

def write_report_to_markdown(content: str, hostname: str) -> str:
    """
    Writes the provided content to a markdown file.
    Args:
        content (str): The markdown content to write.
        filename (str, optional): The filename to write to. Defaults to 'security_report.md'.
    Returns:
        str: Confirmation message with the file path.
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"reports/security_report_{hostname}_{timestamp}.md"

    with open(filename, "w") as f:
        f.write(content)
    return f"Report written to {os.path.abspath(filename)}"