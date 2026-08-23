import json
import re

with open("demo_10_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def clean_text(text):
    # Remove examtopics URLs and broken URL lines
    text = re.sub(r'https?://\S+', '', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.endswith('.html') or 'discussions/amazon' in stripped or 'ions-architect' in stripped or 'reference_policies' in stripped:
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    # Remove multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

md_output = """# 📘 AWS SAA-C03 기출문제 데모 학습 노트 (Q1 ~ Q10)

> **총 725개 문항 중 1~10번 문항 추출 및 정밀 분석 데모**  
> PDF에서 추출한 원문 문제, 선택지, 정답 및 핵심 아키텍처 해설을 수록했습니다.

---

### 📊 Q1 ~ Q10 핵심 출제 토픽 요약

| 문제 번호 | 주요 AWS 서비스 / 토픽 | 핵심 아키텍처 키워드 | 정답 |
|:---:|:---|:---|:---:|
| **Q1** | **Amazon S3 Transfer Acceleration** | 글로벌 사이트 대용량(500GB/일) 고속 집계, 최소 운영 복잡성 | **A** |
| **Q2** | **Amazon Athena** | S3에 저장된 JSON 로그 대상 On-Demand/간단 SQL 쿼리, 최소 변경 | **C** |
| **Q3** | **AWS Organizations & IAM Policy** | `aws:PrincipalOrgID` 조건 키로 조직 내 계정 사용자만 S3 접근 허용 | **A** |
| **Q4** | **VPC Gateway Endpoint (S3)** | 프라이빗 서브넷 EC2에서 인터넷 연결 없이 S3 프라이빗 통신 | **A** |
| **Q5** | **Amazon EFS** | 멀티 AZ EC2 간 공유 파일 스토리지 (EBS는 단일 AZ 전용 한계 극복) | **C** |
| **Q6** | **AWS Snowball Edge** | 70TB 대용량 오프라인 마이그레이션, 네트워크 대역폭 사용 최소화 | **B** |
| **Q7** | **Amazon SNS + SQS (Fan-out)** | 초당 100,000건 스파이크 부하 분리(Decoupling) 및 다중 컨슈머 확장 | **D** |
| **Q8** | **Amazon SQS + EC2 Auto Scaling** | 큐 대기열 크기(Queue Size) 기반 확장으로 탄력성/확장성 극대화 | **B** |
| **Q9** | **AWS Storage Gateway (S3 File Gateway)** | 온프레미스 SMB 파일 서버 용량 확장 + 7일 후 Glacier 수명 주기 관리 | **B** |
| **Q10** | **Amazon SQS FIFO + AWS Lambda** | 전자상거래 주문의 선입선출(First-In-First-Out) 순서 보장 처리 | **B** |

---
"""

for q in questions:
    num = q["number"]
    content = q["content"]
    
    # Split content before Answer: and after
    parts = re.split(r'Answer:\s*([A-E,\s]+)', content, maxsplit=1)
    
    q_and_options = clean_text(parts[0])
    ans_text = parts[1].strip() if len(parts) > 1 else "N/A"
    explanation_part = parts[2].strip() if len(parts) > 2 else ""
    explanation_clean = clean_text(explanation_part)
    
    # Format explanation headers
    explanation_clean = re.sub(r'설명(?:\d+)?:・?', '\n#### 💡 상세 해설\n', explanation_clean)
    
    md_output += f"\n## 📌 문제 {num:02d}\n\n"
    md_output += f"{q_and_options}\n\n"
    md_output += f"> **정답: `{ans_text}`**\n\n"
    if explanation_clean:
        md_output += f"{explanation_clean}\n\n"
    md_output += "---\n"

with open("AWS_SAA_C03_Demo_10Questions.md", "w", encoding="utf-8") as f:
    f.write(md_output)

print("Updated AWS_SAA_C03_Demo_10Questions.md successfully.")
