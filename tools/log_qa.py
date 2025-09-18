import json
import sys
from datetime import datetime

# Simple QA logger: append JSON lines to ../qa/qa_history.jsonl
# Usage: python tools/log_qa.py "question text" "answer text" [username]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python tools/log_qa.py \"question\" \"answer\" [user]")
        sys.exit(1)
    question = sys.argv[1]
    answer = sys.argv[2]
    user = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    entry = {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "user": user,
        "question": question,
        "answer": answer
    }
    out_path = "qa/qa_history.jsonl"
    # Ensure directory exists
    try:
        import os
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    except Exception:
        pass
    with open(out_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print("Logged QA entry to", out_path)
