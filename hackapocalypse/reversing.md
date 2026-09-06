# Example – use the real addresses
xxd -s 0x???? -l 64 ringtrue   # L0_W
xxd -s 0x???? -l 32 ringtrue   # L0_B
xxd -s 0x???? -l 64 ringtrue   # L1_W
xxd -s 0x???? -l 32 ringtrue   # L1_B
xxd -s 0x???? -l 64 ringtrue   # L2_W
xxd -s 0x???? -l 32 ringtrue   # L2_B
xxd -s 0x5060 -l 64 ringtrue   # ECHO_S (we already have part of it)

└─$ nm -C ringtrue | grep -E 'L0_W|L0_B|L1_W|L1_B|L2_W|L2_B|ECHO_S'
0000000000005060 D ECHO_S
00000000000050e0 D L0_B
0000000000005180 D L0_W
00000000000050c0 D L1_B
0000000000005140 D L1_W
00000000000050a0 D L2_B
0000000000005100 D L2_W

xxd -s 0x5060 -l 64 ringtrue   # ECHO_S
xxd -s 0x50a0 -l 32 ringtrue   # L2_B
xxd -s 0x50c0 -l 32 ringtrue   # L1_B
xxd -s 0x50e0 -l 32 ringtrue   # L0_B
xxd -s 0x5100 -l 64 ringtrue   # L2_W
xxd -s 0x5140 -l 64 ringtrue   # L1_W
xxd -s 0x5180 -l 64 ringtrue   # L0_W