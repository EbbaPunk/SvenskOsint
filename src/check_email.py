import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.all import check_all

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else ""
    personnummer = sys.argv[2] if len(sys.argv) > 2 else ""
    if not email:
        print(json.dumps({"error": "no email provided"}))
        sys.exit(1)
    try:
        result = check_all(email, personnummer=personnummer)
        print(json.dumps(result, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
