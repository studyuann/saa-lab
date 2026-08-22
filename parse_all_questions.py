import pymupdf
import re
import json
import os

pdf_path = r"C:\Users\ANN\Downloads\SAA-C03_Examtopics_V18.35_KOR (3).pdf"
doc = pymupdf.open(pdf_path)

print(f"Total PDF pages: {len(doc)}")

full_text = ""
for i, page in enumerate(doc):
    full_text += f"\n---PAGE_{i+1}---\n" + page.get_text()

# Regex to find all Q<number> markers
# Pattern: \nQ(\d+)\s*\n
q_matches = list(re.finditer(r'(?:^|\n)Q(\d+)\s*\n', full_text))
print(f"Found {len(q_matches)} question markers.")

# Tag keyword definitions
TAG_RULES = [
    # Storage
    ("Storage / S3", ["S3", "버킷", "Bucket", "Glacier", "글레이셔", "S3 Transfer Acceleration", "Lifecycle", "수명 주기"]),
    ("Storage / EFS", ["EFS", "Elastic File System", "NFS"]),
    ("Storage / EBS", ["EBS", "Elastic Block Store", "IOPS", "gp2", "gp3", "볼륨"]),
    ("Storage / FSx", ["FSx", "Lustre", "Windows File Server"]),
    ("Storage / Gateway", ["Storage Gateway", "스토리지 게이트웨이", "File Gateway", "Volume Gateway"]),
    ("Migration / Snowball", ["Snowball", "Snowcone", "Snowmobile", "스노우볼", "DataSync", "DMS"]),
    
    # Compute & Serverless
    ("Compute / EC2", ["EC2", "인스턴스", "AMI", "스팟", "Spot", "온디맨드", "On-Demand"]),
    ("Compute / Auto Scaling", ["Auto Scaling", "오토 스케일링", "Target Tracking", "조정 정책"]),
    ("Serverless / Lambda", ["Lambda", "람다", "Serverless", "서버리스"]),
    ("Containers / ECS & EKS", ["ECS", "EKS", "Fargate", "파게이트", "Docker", "컨테이너"]),
    
    # Database
    ("Database / RDS & Aurora", ["RDS", "Aurora", "오로라", "Multi-AZ", "다중 AZ", "읽기 전용 복제본", "Read Replica"]),
    ("Database / DynamoDB", ["DynamoDB", "다이나모", "DAX", "NoSQL", "Global Table", "글로벌 테이블"]),
    ("Database / ElastiCache", ["ElastiCache", "Redis", "Memcached", "캐시", "Cache"]),
    ("Database / Redshift", ["Redshift", "레드시프트", "데이터 웨어하우스", "DW"]),
    
    # Network
    ("Network / VPC", ["VPC", "서브넷", "Subnet", "라우팅", "Route Table", "CIDR", "IGW", "인터넷 게이트웨이", "NAT"]),
    ("Network / Endpoint", ["VPC 엔드포인트", "VPC Endpoint", "PrivateLink", "Gateway Endpoint", "Interface Endpoint"]),
    ("Network / Peering & TGW", ["VPC 피어링", "VPC Peering", "Transit Gateway", "트랜짓 게이트웨이"]),
    ("Network / CloudFront", ["CloudFront", "클라우드프론트", "CDN", "Edge Location", "엣지 로케이션"]),
    ("Network / Route 53", ["Route 53", "DNS", "Latency Routing", "Failover", "지연 시간 라우팅", "장애 조치"]),
    ("Network / Load Balancer", ["ALB", "NLB", "Application Load Balancer", "Network Load Balancer", "로드 밸런서"]),
    ("Network / Hybrid", ["Direct Connect", "다이렉트 커넥트", "VPN", "Site-to-Site"]),

    # Security & Management
    ("Security / IAM", ["IAM", "역할", "Role", "정책", "Policy", "MFA", "보안 주체", "Principal"]),
    ("Security / KMS & Secrets", ["KMS", "Secrets Manager", "시크릿 매니저", "암호화", "Key Management"]),
    ("Security / Compliance & WAF", ["WAF", "Shield", "GuardDuty", "Security Hub", "Inspector", "Macie"]),
    ("Management / Organizations", ["Organizations", "SCP", "조직 단위", "OU", "Control Tower"]),
    ("Management / Monitoring", ["CloudWatch", "CloudTrail", "클라우드워치", "클라우드트레일", "Config", "X-Ray"]),

    # Messaging & Integration
    ("Messaging / SQS", ["SQS", "대기열", "Queue", "FIFO", "Dead-Letter", "DLQ"]),
    ("Messaging / SNS", ["SNS", "주제", "Topic", "알림", "Notification"]),
    ("Messaging / EventBridge", ["EventBridge", "Event", "이벤트브릿지"]),
    ("Analytics / Athena & Glue", ["Athena", "아테나", "Glue", "EMR", "Kinesis", "키네시스", "QuickSight"])
]

def clean_text(text):
    text = re.sub(r'---PAGE_\d+---', '', text)
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

def determine_tags(text):
    tags = []
    for tag_name, keywords in TAG_RULES:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE) or (len(kw) >= 2 and kw in text):
                tags.append(tag_name)
                break
    if not tags:
        tags.append("General AWS / Architecture")
    return tags[:4] # max 4 tags

questions_data = []

for i, match in enumerate(q_matches):
    start = match.start()
    end = q_matches[i+1].start() if i+1 < len(q_matches) else len(full_text)
    q_num = int(match.group(1))
    raw_content = full_text[start:end].strip()
    
    # Split content before and after Answer:
    parts = re.split(r'Answer:\s*([A-E,\s]+)', raw_content, maxsplit=1)
    q_and_options = clean_text(parts[0])
    ans_text = parts[1].strip() if len(parts) > 1 else ""
    explanation_raw = parts[2].strip() if len(parts) > 2 else ""
    explanation = clean_text(explanation_raw)
    explanation = re.sub(r'설명(?:\d+)?:・?', '\n', explanation).strip()
    
    # Extract choices
    lines = q_and_options.split('\n')
    body_lines = []
    choices = {}
    current_choice = None
    
    for line in lines:
        line_s = line.strip()
        if re.match(r'^Q\d+', line_s):
            continue
        
        choice_match = re.match(r'^([A-F])\.\s*(.*)', line_s)
        if choice_match:
            current_choice = choice_match.group(1)
            choices[current_choice] = choice_match.group(2)
        elif current_choice:
            choices[current_choice] += " " + line_s
        else:
            body_lines.append(line_s)
            
    question_text = " ".join([l for l in body_lines if l]).strip()
    
    # Clean up whitespace in choices
    for k in choices:
        choices[k] = re.sub(r'\s+', ' ', choices[k]).strip()
        
    full_searchable = f"{question_text} {' '.join(choices.values())} {explanation}"
    tags = determine_tags(full_searchable)
    
    questions_data.append({
        "id": q_num,
        "number": q_num,
        "title": f"문항 {q_num:03d}",
        "question": question_text,
        "choices": choices,
        "answer": ans_text.replace(" ", ""),
        "explanation": explanation,
        "tags": tags
    })

# Sort by question number
questions_data.sort(key=lambda x: x["number"])

with open("quiz_data.json", "w", encoding="utf-8") as f:
    json.dump(questions_data, f, ensure_ascii=False, indent=2)

print(f"Successfully processed and saved {len(questions_data)} questions to quiz_data.json!")
