from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
import os
import re

# --- Markdown bold parser ---
def split_bold_parts(text):
    pattern = r"\*\*(.*?)\*\*"
    parts = []
    last_end = 0
    for match in re.finditer(pattern, text):
        start, end = match.span()
        if start > last_end:
            parts.append((text[last_end:start], False))
        parts.append((match.group(1), True))
        last_end = end
    if last_end < len(text):
        parts.append((text[last_end:], False))
    return parts

# --- Wrapped + bold text drawer with optional label ---
def draw_rich_text_wrapped(c, x, y, text, max_width, font_size=12, label=None):
    parts = split_bold_parts(text)
    line = []
    current_line_width = 0
    lines = []
    tab_space = 10

    label_width = 0
    if label:
        c.setFont("Helvetica-Bold", font_size)
        label_width = c.stringWidth(label + ".", "Helvetica-Bold", font_size) + tab_space

    for text_part, is_bold in parts:
        words = text_part.split(" ")
        for word in words:
            word += " "
            font = "Helvetica-Bold" if is_bold else "Helvetica"
            width = c.stringWidth(word, font, font_size)
            if current_line_width + width > max_width - label_width and line:
                lines.append(line)
                line = []
                current_line_width = 0
            line.append((word, is_bold))
            current_line_width += width
    if line:
        lines.append(line)

    for idx, line in enumerate(lines):
        cursor_x = x
        if idx == 0 and label:
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(cursor_x, y, label + ".")
            cursor_x += label_width
        for word, is_bold in line:
            font = "Helvetica-Bold" if is_bold else "Helvetica"
            c.setFont(font, font_size)
            c.drawString(cursor_x, y, word)
            cursor_x += c.stringWidth(word, font, font_size)
        y -= font_size + 4
    return y

# --- Draw oval in rectangle ---
def draw_oval_in_rect(c, x, y, width=14, height=10):
    c.rect(x, y, width, height)
    inset = 2
    c.ellipse(x + inset, y + inset, x + width - inset, y + height - inset)

# --- Parse markdown ---
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

# --- Create PDF ---
def create_pdf(md_path):
    base_name = os.path.splitext(md_path)[0]
    output_pdf = base_name + ".pdf"

    questions = parse_md(md_path)
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4

    margin_top = 20 * mm
    margin_bottom = 20 * mm
    margin_left = 10 * mm  # margin for digit boxes
    margin_right = 20 * mm

    y = page_height - margin_top
    question_number = 1

    qnum_box_width = 12
    box_height = 16
    spacing_between_boxes = 0  # boxes touching each other
    total_qnum_width = qnum_box_width * 2 + spacing_between_boxes
    gap_after_boxes = 12  # extra gap between boxes and question text
    text_start_x = margin_left + total_qnum_width + gap_after_boxes
    max_text_width = page_width - text_start_x - margin_right - 40  # space for option ovals

    for q in questions:
        qnum = f"{question_number:02}"
        box_y = y - 4

        # Draw two digit boxes for question number
        c.setFont("Helvetica-Bold", 12)
        c.setLineWidth(0.5)

        # First digit box: at margin_left
        box_x1 = margin_left
        c.rect(box_x1, box_y, qnum_box_width, box_height)
        c.drawCentredString(box_x1 + qnum_box_width / 2, box_y + 3, qnum[0])

        # Second digit box: touching first box
        box_x2 = margin_left + qnum_box_width + spacing_between_boxes
        c.rect(box_x2, box_y, qnum_box_width, box_height)
        c.drawCentredString(box_x2 + qnum_box_width / 2, box_y + 3, qnum[1])

        # Draw question text after boxes + gap
        question_text = q["question"]
        y = draw_rich_text_wrapped(c, text_start_x, y, question_text, max_width=max_text_width, font_size=14)
        y -= 6

        option_labels = ['A', 'B', 'C', 'D']
        for i, option in enumerate(q['options']):
            y_before = y
            y = draw_rich_text_wrapped(
                c, text_start_x + 10, y, option,
                max_width=max_text_width - 10,
                font_size=12,
                label=option_labels[i]
            )
            c.rect(page_width - margin_right - 20, y_before - 3, 14, 10)
            c.ellipse(page_width - margin_right - 20 + 2, y_before - 3 + 2, page_width - margin_right - 20 + 14 - 2, y_before - 3 + 10 - 2)

        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#d9d9d9"))
        c.drawRightString(page_width - margin_right, y, "(1 mark)")
        c.setFillColor(HexColor("#000000"))

        y -= 30
        question_number += 1

        if y < margin_bottom + 60:
            c.showPage()
            y = page_height - margin_top
            c.setFont("Helvetica", 12)

    c.save()
    print(f"PDF generated: {output_pdf}")

# --- CLI ---
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python mcqs.py input.md")
    else:
        create_pdf(sys.argv[1])
