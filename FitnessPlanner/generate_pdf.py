from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def generate_pdf():
    # Create PDF document
    doc = SimpleDocTemplate("project_code.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom style for file names
    file_style = ParagraphStyle(
        'FileStyle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20
    )
    
    # Custom style for code
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontSize=8,
        leading=10,
        fontName='Courier'
    )
    
    # Get all relevant files
    relevant_extensions = {'.py', '.html', '.css', '.js'}
    files = [f for f in os.listdir('.') if os.path.isfile(f) and 
             os.path.splitext(f)[1].lower() in relevant_extensions]
    
    # Add each file to the PDF
    for file_name in files:
        # Add file name as heading
        story.append(Paragraph(f"File: {file_name}", file_style))
        
        # Add file content
        content = read_file_content(file_name)
        story.append(Paragraph(content, code_style))
        
        # Add page break
        story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(story)

if __name__ == "__main__":
    generate_pdf() 