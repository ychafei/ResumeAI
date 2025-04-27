import PyPDF2
import docx

def extract_text(file):
    """Extracts text from uploaded PDF or DOCX files."""
    
    filename = file.filename.lower()  # ✅ Get filename

    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file.stream)  # ✅ Use file.stream
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() if page.extract_text() else ''
        return text

    elif filename.endswith('.docx'):
        doc = docx.Document(file.stream)  # ✅ Use file.stream  
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text

    else:
        return "Unsupported file format"
