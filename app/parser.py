from PyPDF2 import PdfFileReader
from io import BytesIO


def parse_document(content):
    """
    Parses the content of a PDF document and extracts the text.

    This function takes the binary content of a PDF file, reads it, and extracts
    the text from each page.

    :param content: (bytes) The binary content of the PDF document.
    :return: (str) The extracted text from the PDF document.
    """
    # Example for PDF parsing
    reader = PdfFileReader(BytesIO(content))
    text = ''
    for page in range(reader.numPages):
        text += reader.getPage(page).extract_text()
    return text
