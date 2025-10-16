#!/usr/bin/env python3
"""
dns_plain_sender.py

SAFE PoC: send an explicit payload (provided on the command line) as DNS A queries.
This script DOES NOT read any files. You MUST provide the payload explicitly.

Behavior:
 - Minimal sanitization: replaces characters not allowed in DNS labels with '-'
 - Splits the sanitized payload into labels (max_label_len, default 60)
 - Sends queries named: <label>.<index>.<domain>
 - Sends each query as a raw UDP DNS A query to the server IP you specify

Usage example:
  python3 dns_plain_sender.py --server 198.51.100.12 --domain testlog.sdrtest.site \
      --payload "MY TEST PAYLOAD 123" --delay 0.2

Notes:
 - DNS label max length is 63 bytes; script uses default 60 for safety
 - Entire qname length must be <= 255 bytes; keep payloads small or chunk into many queries
 - This tool is intentionally explicit: you type/paste what you want to send
"""
import argparse, socket, struct, random, time, re, sys

def sanitize_payload(s, max_label_len=60):
    # Replace disallowed characters: allow a-z, 0-9, and hyphen.
    # Convert to lower-case. Consecutive disallowed characters become single '-'.
    s = s.lower()
    # replace whitespace and non-alnum/hyphen with '-'
    s = re.sub(r'[^a-z0-9-]+', '-', s)
    # collapse multiple '-' into one
    s = re.sub(r'-{2,}', '-', s).strip('-')
    if not s:
        return []
    # split into label-sized chunks
    labels = [s[i:i+max_label_len] for i in range(0, len(s), max_label_len)]
    return labels

def build_dns_query(qname, qtype=1):
    # Build a minimal DNS query packet (standard query, recursion desired)
    tid = random.randint(0, 0xffff)
    header = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 0)  # flags: RD
    qparts = b''
    for part in qname.split('.'):
        if len(part) == 0:
            continue
        if len(part) > 63:
            raise ValueError("label too long: %s" % part)
        qparts += bytes([len(part)]) + part.encode('ascii', errors='ignore')
    qparts += b'\x00'  # end of qname
    qtype_qclass = struct.pack("!HH", qtype, 1)  # type A, class IN
    return header + qparts + qtype_qclass

def send_udp(pkt, server_ip, timeout=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(pkt, (server_ip, 53))
        try:
            data, _ = s.recvfrom(2048)
            return True, len(data)
        except socket.timeout:
            return True, "no response (timeout)"
    except Exception as e:
        return False, str(e)
    finally:
        s.close()

def main():
    p = argparse.ArgumentParser(description="Send explicit payload text as DNS query labels (safe PoC).")
    p.add_argument("--server", required=True, help="DNS server IP to send queries to (e.g. authoritative server IP)")
    p.add_argument("--domain", required=True, help="Your authoritative domain (e.g. logs.example.com)")
    p.add_argument("--payload", required=True, help="Explicit payload text to send (you must provide it)")
    p.add_argument("--label-len", type=int, default=60, help="Max label length (default 60, <=63)")
    p.add_argument("--delay", type=float, default=0.15, help="Delay between queries (seconds)")
    p.add_argument("--prefix", default="", help="Optional prefix label to add before payload labels")
    args = p.parse_args()

    if args.label_len < 1 or args.label_len > 63:
        print("label-len must be between 1 and 63", file=sys.stderr)
        sys.exit(2)

    labels = sanitize_payload(args.payload, max_label_len=args.label_len)
    if not labels:
        print("Payload sanitized to empty string; nothing to send. Provide a payload with letters/numbers.", file=sys.stderr)
        sys.exit(1)

    print(f"Prepared {len(labels)} label(s) to send to {args.server} under domain {args.domain}")
    for idx, lab in enumerate(labels):
        # qname: optionally prefix, then label.index.domain
        parts = []
        if args.prefix:
            parts.append(args.prefix)
        parts.append(lab)
        parts.append(str(idx))
        parts.append(args.domain)
        qname = ".".join(parts)
        # warn if qname too long
        if len(qname) > 255:
            print(f"Skipping chunk {idx}: qname too long ({len(qname)} > 255): {qname[:80]}...", file=sys.stderr)
            continue
        try:
            pkt = build_dns_query(qname)
        except ValueError as e:
            print("Error building query:", e, file=sys.stderr)
            continue
        ok, info = send_udp(pkt, args.server)
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  QUERY -> {qname}  : {ok} {info}")
        time.sleep(args.delay)
    print("Done.")

if __name__ == "__main__":
    main()
