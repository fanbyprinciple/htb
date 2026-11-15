
#!/usr/bin/env python3
from pwn import *
import re

# Choose ONE connection method:
# io = process(["python3", "dice.py"])  # Local challenge
io = remote("154.57.164.82", 38038)                # Remote CTF server

context.log_level = "error"

dice_pattern = re.compile(
    rb"Player\s+(\d+):\s+([1-6](?:\s+[1-6])*)"
)

# Start the game by answering Yes.
io.recvuntil(b"> ")
io.sendline(b"1")

for rnd in range(100):
    scores = {}
    
    # Read every line until the winner question appears.
    while True:
        line = io.recvline()

        if b"Who wins this round?" in line:
            break

        match = dice_pattern.search(line)
        if match:
            player = int(match.group(1))
            dice = list(map(int, match.group(2).split()))
            scores[player] = sum(dice)

    if not scores:
        print(f"Could not parse round {rnd + 1}")
        break

    # Highest score wins. In a tie, the LAST player wins.
    winner = max(scores, key=lambda p: (scores[p], p))

    # Submit immediately to beat the 0.3-second timeout.
    io.sendline(str(winner).encode())

    print(
        f"Round {rnd + 1}: "
        f"winner = Player {winner}, "
        f"score = {scores[winner]}"
    )

# Print the flag or any final server output.
print(io.recvall(timeout=5).decode(errors="replace"))
