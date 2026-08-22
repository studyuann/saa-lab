import json
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def run_cli_quiz():
    try:
        with open("quiz_data.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
    except Exception as e:
        print(f"Error loading quiz_data.json: {e}")
        return

    print("=" * 60)
    print(" AWS SAA-C03 터미널 퀴즈 (Q01 ~ Q10 데모)")
    print("=" * 60)
    print("명령어: A/B/C/D (답 선택), Q (종료), H (해설보기)")
    print("-" * 60)

    score = 0
    wrong_list = []

    for i, q in enumerate(questions):
        print(f"\n[문제 {q['number']}/10] (태그: {', '.join(q['tags'])})")
        print(f"{q['question']}\n")
        
        for k in ['A', 'B', 'C', 'D']:
            if k in q['choices']:
                print(f"  {k}. {q['choices'][k]}")
        
        while True:
            ans = input("\n👉 정답을 입력하세요 (A/B/C/D): ").strip().upper()
            if ans == 'Q':
                print("\n퀴즈를 종료합니다.")
                return
            if ans in ['A', 'B', 'C', 'D']:
                break
            print("올바른 보기(A, B, C, D)를 입력해주세요.")

        if ans == q['answer']:
            print(f"\n🎉 [정답!] (입력: {ans} / 정답: {q['answer']})")
            score += 1
        else:
            print(f"\n❌ [오답!] (입력: {ans} / 정답: {q['answer']})")
            wrong_list.append(q['number'])

        print("\n[💡 핵심 해설]")
        print(q['explanation'])
        print("-" * 60)
        input("엔터를 누르면 다음 문제로 넘어갑니다...")

    print("\n" + "=" * 60)
    print(f"🏁 퀴즈 완료! 최종 점수: {score} / {len(questions)} ({int(score/len(questions)*100)}%)")
    if wrong_list:
        print(f"❌ 틀린 문제 번호: {wrong_list}")
    else:
        print("🎉 만점입니다! 축하드립니다!")
    print("=" * 60)

if __name__ == "__main__":
    run_cli_quiz()
