import json
import re

with open("demo_10_questions.json", "r", encoding="utf-8") as f:
    raw_questions = json.load(f)

tag_mapping = {
    1: ["Storage / S3", "Network / Transfer", "Performance"],
    2: ["Analytics / Athena", "Storage / S3", "Serverless"],
    3: ["Security / IAM", "Management / Organizations", "Storage / S3"],
    4: ["Network / VPC", "Storage / S3", "VPC Endpoint"],
    5: ["Storage / EFS", "Compute / EC2", "High Availability"],
    6: ["Migration / Snowball", "Storage / S3", "Cost Optimization"],
    7: ["Messaging / SNS & SQS", "Decoupling", "Scalability"],
    8: ["Compute / Auto Scaling", "Messaging / SQS", "Reliability"],
    9: ["Hybrid / Storage Gateway", "Storage / Glacier", "Lifecycle"],
    10: ["Serverless / Lambda", "Messaging / SQS FIFO", "API Gateway"]
}

def clean_text(text):
    text = re.sub(r'https?://\S+', '', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.endswith('.html') or 'discussions/amazon' in stripped or 'ions-architect' in stripped or 'reference_policies' in stripped:
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

parsed_items = []

for q in raw_questions:
    num = q["number"]
    content = q["content"]
    
    # Split content by Answer:
    parts = re.split(r'Answer:\s*([A-E,\s]+)', content, maxsplit=1)
    q_and_options = clean_text(parts[0])
    ans_text = parts[1].strip() if len(parts) > 1 else ""
    explanation_raw = parts[2].strip() if len(parts) > 2 else ""
    explanation = clean_text(explanation_raw)
    explanation = re.sub(r'설명(?:\d+)?:・?', '\n', explanation).strip()
    
    # Extract question text and choices A, B, C, D
    # We look for A., B., C., D.
    q_lines = q_and_options.split('\n')
    
    # First line usually Q1
    body_lines = []
    choices = {}
    current_choice = None
    
    for line in q_lines:
        line_s = line.strip()
        if re.match(r'^Q\d+', line_s):
            continue
        
        choice_match = re.match(r'^([A-E])\.\s*(.*)', line_s)
        if choice_match:
            current_choice = choice_match.group(1)
            choices[current_choice] = choice_match.group(2)
        elif current_choice:
            choices[current_choice] += " " + line_s
        else:
            body_lines.append(line_s)
            
    question_text = " ".join([l for l in body_lines if l]).strip()
    
    parsed_items.append({
        "id": num,
        "number": num,
        "title": f"문항 {num:02d}",
        "question": question_text,
        "choices": choices,
        "answer": ans_text,
        "explanation": explanation,
        "tags": tag_mapping.get(num, ["General AWS"])
    })

with open("quiz_data.json", "w", encoding="utf-8") as f:
    json.dump(parsed_items, f, ensure_ascii=False, indent=2)

print(f"Generated quiz_data.json with {len(parsed_items)} questions.")
