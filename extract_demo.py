import pymupdf
import re
import json

pdf_path = r"C:\Users\ANN\Downloads\SAA-C03_Examtopics_V18.35_KOR (3).pdf"
doc = pymupdf.open(pdf_path)

# Extract first few pages to see how questions are structured
text_pages = []
for i in range(min(25, len(doc))):
    text_pages.append(doc[i].get_text())

full_text = "\n---PAGE---\n".join(text_pages)

with open("sample_pages.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Extracted {len(text_pages)} pages. Check sample_pages.txt")
