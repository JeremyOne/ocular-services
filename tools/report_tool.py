import os
import time
import markdown
import pdfkit

def write_report(content: str, hostname: str) -> str:
    """
    Writes the provided content to a markdown file.
    Args:
        content (str): The markdown content to write.
        filename (str, optional): The filename to write to. Defaults to 'security_report.md'.
    Returns:
        str: Confirmation message with the file path.
    """

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"reports/{hostname}_{timestamp}.md"

    with open(filename, "w") as f:
        f.write(content)

    # Also convert the markdown to PDF 
    markdown_export(filename)

    return f"Report written to {os.path.abspath(filename)}"



def markdown_export(markdown_path: str, pdf_path: str = None, html_path: str = None) -> str:
    """
    Converts a Markdown file to a PDF file.
    Args:
        markdown_path (str): Path to the input Markdown file.
        pdf_path (str, optional): Path to the output PDF file. If not provided, uses the same name as the markdown file.
    Returns:
        str: Path to the generated PDF file or error message.
    """
    if not os.path.isfile(markdown_path):
        return f"Markdown file not found: {markdown_path}"

    if pdf_path is None:
        pdf_path = os.path.splitext(markdown_path)[0] + ".pdf"

    if html_path is None:
        html_path = os.path.splitext(markdown_path)[0] + ".html"

    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        html_content = markdown.markdown(md_content, output_format="html5")

        # Save PDF
        pdfkit.from_string(html_content, pdf_path)

        # Save HTML
        with open(html_path, "w") as f:
            f.write(html_content)

        return pdf_path
    
    except Exception as e:
        return f"Error converting markdown to PDF: {e}"