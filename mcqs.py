from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
import textwrap
import os

def parse_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f.readlines()]

    questions = []
    current_q = {"question": "", "options": []}

    for line in lines:
        if line.strip() == "":
            if current_q["question"]:
                questions.append(current_q)
                current_q = {"question": "", "options": []}
        elif line.strip().startswith("- "):
            current_q["options"].append(line.strip()[2:])
        else:
            if current_q["question"]:
                current_q["question"] += " " + line.strip()
            else:
                current_q["question"] = line.strip()

    if current_q["question"]:
        questions.append(current_q)

    return questions

def draw_oval_in_rect(c, x, y, width=14, height=10):
    c.rect(x, y, width, height)
    inset = 2
    c.ellipse(x + inset, y + inset, x + width - inset, y + height - inset)

def create_pdf(md_path):
    base_name = os.path.splitext(md_path)[0]
    output_pdf = base_name + ".pdf"

    questions = parse_md(md_path)
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4
    margin = 20 * mm
    x_text = margin
    y = page_height - margin
    question_number = 1

    for q in questions:
        c.setFont("Helvetica", 14)
        wrapped = textwrap.wrap(f"Q{question_number}. {q['question']}", width=90)
        for line in wrapped:
            c.drawString(x_text, y, line)
            y -= 16

        y -= 6

        c.setFont("Helvetica", 12)
        option_labels = ['A', 'B', 'C', 'D']
        for i, option in enumerate(q['options']):
            line = f"{option_labels[i]} {option}"
            wrapped_opt = textwrap.wrap(line, width=80)
            for j, line in enumerate(wrapped_opt):
                c.drawString(x_text + 10, y, line)
                if j == 0:
                    draw_oval_in_rect(c, page_width - margin - 20, y - 3, width=14, height=10)
                y -= 14

        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#d9d9d9"))
        c.drawRightString(page_width - margin, y, "(1 mark)")
        c.setFillColor(HexColor("#000000"))

        y -= 30
        question_number += 1

        if y < margin + 60:
            c.showPage()
            y = page_height - margin
            c.setFont("Helvetica", 12)

    c.save()
    print(f"PDF generated: {output_pdf}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python md_to_pdf.py input.md")
    else:
        create_pdf(sys.argv[1])
