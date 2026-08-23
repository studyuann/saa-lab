import pymupdf
import re
import json

pdf_path = r"C:\Users\ANN\Downloads\SAA-C03_Examtopics_V18.35_KOR (3).pdf"
doc = pymupdf.open(pdf_path)

full_text = ""
for page in doc:
    full_text += page.get_text() + "\n"

# Split by question pattern Q1, Q2, etc.
# Pattern: \nQ(\d+)\s*\n
q_matches = list(re.finditer(r'(?:^|\n)Q(\d+)\s*\n', full_text))
print(f"Total questions found by regex: {len(q_matches)}")

questions = []
for i in range(min(10, len(q_matches))):
    start = q_matches[i].start()
    end = q_matches[i+1].start() if i+1 < len(q_matches) else len(full_text)
    q_num = q_matches[i].group(1)
    q_body = full_text[start:end].strip()
    questions.append({
        "number": int(q_num),
        "content": q_body
    })

with open("demo_10_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Saved 10 demo questions to demo_10_questions.json")
