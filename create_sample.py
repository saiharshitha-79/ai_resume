from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

resume_text = """
John Doe
Software Engineer

Experience:
- 3 years of experience as a Python Developer.
- Built backend services using Python, Django, and Flask.
- Worked with databases like PostgreSQL and MySQL.
- Containerized applications using Docker.
- Proficient in Git and Linux.
- Familiar with basic Data Structures and Algorithms.

Education:
- B.S. in Computer Science
"""

for line in resume_text.split('\n'):
    pdf.cell(200, 10, txt=line, ln=1, align='L')

pdf.output("sample_resume.pdf")
print("success")
