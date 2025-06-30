def load_markdown_template(template_path: str = "reports/template.md") -> str:
    """
    Loads the markdown template file into a string variable.
    Args:
        template_path (str): Path to the markdown template file.
    Returns:
        str: Contents of the markdown template file.
    """
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading template: {e}"