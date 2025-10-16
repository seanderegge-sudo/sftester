#!/usr/bin/env python3
"""
egress_probe.py

Comprehensive egress tests to run from a sandbox/container. Use responsibly.
Targets: provide a whitelisted host and a non-whitelisted host (both should be under your control).

Example:
  python3 egress_probe.py --whitelist ec2-107-21-38-89.compute-1.amazonaws.com \
                          --target sdrtest.site \
                          --dns-server 8.8.8.8
"""

import argparse
import socket
import ssl
import sys
import time
import traceback
import subprocess
import threading
import random
import string

TIMEOUT = 6.0  # seconds for socket operations

def now(): return time.strftime("%Y-%m-%d %H:%M:%S")

def banner(title):
    print("\n" + "="*80)
    print(f"{now()}  {title}")
    print("="*80)

def safe_run(cmd, timeout=10):
    """Run subprocess command and capture output; return (rc, out, err)"""
    try:
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, text=True)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return -1, "", f"subprocess error: {e}"

def resolve(host):
    """Return list of (family, addr) tuples from getaddrinfo"""
    out = []
    try:
        for res in socket.getaddrinfo(host, None, 0, socket.SOCK_STREAM):
            fam, _, _, _, sa = res
            ip = sa[0]
            out.append((fam, ip))
    except Exception as e:
        return False, str(e)
    return True, out

def tcp_connect(host, port, family=socket.AF_INET, timeout=TIMEOUT):
    s = None
    try:
        s = socket.socket(family, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return True, "connected"
    except Exception as e:
        return False, repr(e)
    finally:
        if s:
            try: s.close()
            except: pass

def tls_probe(hostname, connect_addr, port=443, sni_hostname=None, family=socket.AF_INET):
    """Establish TLS and return cipher and cert details"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        # Connect raw
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((connect_addr, port))
        # Wrap with SNI if provided, else use hostname
        server_hostname = sni_hostname if sni_hostname is not None else hostname
        ss = ctx.wrap_socket(sock, server_hostname=server_hostname)
        cert = ss.getpeercert()
        cipher = ss.cipher()
        proto = ss.version()
        ss.close()
        return True, {"protocol": proto, "cipher": cipher, "cert_subject": cert.get('subject'), "issuer": cert.get('issuer')}
    except ssl.SSLError as e:
        return False, f"ssl error: {e}"
    except Exception as e:
        return False, f"error: {e}"

def http_get(host, port=80, use_tls=False, host_header=None, family=socket.AF_INET):
    """Simple HTTP GET using sockets to inspect what goes through"""
    try:
        if use_tls:
            port = 443 if port == 80 else port
            success, data = tls_probe(host, host if not is_ip(host) else host, port=port, sni_hostname=host if not is_ip(host) else None, family=family)
            # For TLS we still attempt a GET via ssl socket
            ctx = ssl.create_default_context()
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            sock.connect((host, port))
            ss = ctx.wrap_socket(sock, server_hostname=host if not is_ip(host) else None)
            send_host = host_header if host_header else host
            req = f"GET / HTTP/1.1\r\nHost: {send_host}\r\nConnection: close\r\nUser-Agent: egress-probe\r\n\r\n"
            ss.send(req.encode())
            r = b""
            while True:
                chunk = ss.recv(4096)
                if not chunk: break
                r += chunk
            ss.close()
            return True, r.decode(errors='replace')[:4000]
        else:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            sock.connect((host, port))
            send_host = host_header if host_header else host
            req = f"GET / HTTP/1.1\r\nHost: {send_host}\r\nConnection: close\r\nUser-Agent: egress-probe\r\n\r\n"
            sock.send(req.encode())
            r = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk: break
                r += chunk
            sock.close()
            return True, r.decode(errors='replace')[:4000]
    except Exception as e:
        return False, repr(e)

def is_ip(s):
    try:
        socket.inet_pton(socket.AF_INET, s)
        return True
    except Exception:
        try:
            socket.inet_pton(socket.AF_INET6, s)
            return True
        except Exception:
            return False

def udp_send(dst_ip, dst_port, payload=b"egress-probe", timeout=3):
    """Send a single UDP packet and wait for possible reply (non-blocking)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(payload, (dst_ip, dst_port))
        # try recv
        try:
            data, addr = s.recvfrom(4096)
            return True, f"recv from {addr}: {data[:200]!r}"
        except socket.timeout:
            return True, "sent, no reply (timeout)"
    except Exception as e:
        return False, repr(e)
    finally:
        s.close()

def dns_query_udp(dns_server, qname, timeout=3):
    """
    Very small DNS UDP query to dns_server for qname A record; does not depend on dnspython.
    Build a minimal DNS packet (no EDNS).
    """
    import struct, random
    try:
        tid = random.randint(0, 0xffff)
        # Header: id, flags (0x0100 standard query), qdcount=1, ancount=0, nscount=0, arcount=0
        header = struct.pack("!HHHHHH", tid, 0x0100, 1, 0, 0, 0)
        # build question qname in labels
        labels = b""
        for part in qname.split("."):
            labels += bytes([len(part)]) + part.encode()
        labels += b"\x00"
        qtype_qclass = struct.pack("!HH", 1, 1)  # A, IN
        pkt = header + labels + qtype_qclass
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        s.sendto(pkt, (dns_server, 53))
        data, _ = s.recvfrom(4096)
        # return hex prefix of response
        return True, {"len": len(data), "hex": data[:200].hex()}
    except Exception as e:
        return False, repr(e)

def test_subprocess_tools(target, whitelisted):
    """Try to run curl and openssl if present with -v to see underlying behaviour"""
    results = {}
    # curl verbose
    rc, out, err = safe_run(f"curl -vI --max-time 10 https://{target}", timeout=15)
    results['curl_head'] = {"rc": rc, "stdout": out[:4000], "stderr": err[:4000]}
    # openssl s_client
    rc2, out2, err2 = safe_run(f"openssl s_client -connect {target}:443 -servername {target} -brief 2>&1", timeout=15)
    results['openssl_s_client'] = {"rc": rc2, "stdout": out2[:4000], "stderr": err2[:4000]}
    return results

def random_label(n=8):
    return ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(n))

def perform_tests(whitelist, target, dns_server=None):
    banner("CONFIGURATION")
    print(f"Whitelist host: {whitelist}")
    print(f"Non-whitelisted target: {target}")
    print(f"Custom DNS server: {dns_server}")
    print(f"Timeouts: socket/TCP={TIMEOUT}s")
    print("Note: outputs truncated for brevity.")

    # Resolve both hosts
    banner("DNS RESOLUTION")
    for h in (whitelist, target):
        ok, res = resolve(h)
        if not ok:
            print(f"[FAIL] Resolve {h}: {res}")
        else:
            print(f"[OK] Resolve {h}: {res}")

    # Resolve using explicit dns server via UDP minimal query (if provided)
    if dns_server:
        banner("DNS SERVER RAW UDP QUERY")
        for h in (whitelist, target):
            q = f"{random_label()}.{h}"
            ok, res = dns_query_udp(dns_server, q)
            if ok:
                print(f"[INFO] Raw DNS query for {q} -> response len {res['len']}, hex-prefix {res['hex'][:200]}")
            else:
                print(f"[FAIL] Raw DNS query to {dns_server} for {q}: {res}")

    # Try connect to port 443 (TLS) for both hostnames and for every resolved IP
    banner("TLS CONNECT & SNI TESTS")
    for h in (whitelist, target):
        ok, items = resolve(h)
        if not ok:
            print(f"[SKIP] {h} resolution failed earlier: {items}")
            continue
        print(f"Host {h} -> addresses: {items}")
        for fam, ip in items:
            fam_name = "IPv6" if fam == socket.AF_INET6 else "IPv4"
            print(f"\n[TEST] TLS connect to {ip} (family={fam_name}) using SNI={h}")
            succ, info = tls_probe(h, ip, port=443, sni_hostname=h if not is_ip(h) else None, family=fam)
            if succ:
                print(f"[OK] TLS ok -> proto={info['protocol']} cipher={info['cipher']} cert_subject={info['cert_subject'][:3]}")
            else:
                print(f"[FAIL] TLS connect to {ip} SNI={h} : {info}")

            print(f"[TEST] TLS connect to {ip} using SNI=not-{h}")
            succ2, info2 = tls_probe(h, ip, port=443, sni_hostname="not-"+h, family=fam)
            if succ2:
                print(f"[OK] TLS ok with different SNI (!) -> {info2}")
            else:
                print(f"[INFO] TLS with different SNI failed (expected): {info2}")

    # HTTP GET variety: host header tricks, connect by IP:443 + Host header
    banner("HTTP/HTTPS GETS - host header / by-IP tests")
    for h in (whitelist, target):
        ok, addrs = resolve(h)
        if not ok:
            print(f"[SKIP] {h} resolution failed earlier.")
            continue
        for fam, ip in addrs:
            fam_name = "IPv6" if fam == socket.AF_INET6 else "IPv4"
            print(f"\n[TEST] Plain HTTP GET to {ip}:80 with Host: {h} (family={fam_name})")
            succ, out = http_get(ip, port=80, use_tls=False, host_header=h, family=fam)
            print(f"{'[OK]' if succ else '[FAIL]'} -> {out if succ else out}")

            print(f"[TEST] HTTPS GET to {ip}:443 with Host: {h} (SNI= {h if not is_ip(h) else 'none'})")
            succ, out = http_get(ip, port=443, use_tls=True, host_header=h, family=fam)
            print(f"{'[OK]' if succ else '[FAIL]'} -> {out if succ else out}")

            # Try with Host header set to whitelisted host while connecting to non-whitelisted IP
            alt_host = whitelist if h == target else target
            print(f"[TEST] HTTPS GET to {ip}:443 but Host header {alt_host} (host-header confusion test)")
            succ, out = http_get(ip, port=443, use_tls=True, host_header=alt_host, family=fam)
            print(f"{'[OK]' if succ else '[FAIL]'} -> {out if succ else out}")

    # Try IPv6 explicit if addresses exist
    banner("IPv6 SPECIFIC TESTS")
    for h in (whitelist, target):
        try:
            info6 = socket.getaddrinfo(h, 443, socket.AF_INET6, socket.SOCK_STREAM)
            if info6:
                print(f"[INFO] {h} has IPv6 addresses: {[a[4][0] for a in info6]}")
            for res in info6:
                ip6 = res[4][0]
                print(f"[TEST] TLS connect to IPv6 {ip6}")
                succ, info = tls_probe(h, ip6, family=socket.AF_INET6)
                print(f"{'[OK]' if succ else '[FAIL]'} -> {info}")
        except Exception as e:
            print(f"[INFO] IPv6 test for {h} skipped or no IPv6: {e}")

    # Try UDP to port 53 (DNS) and arbitrary UDP to server
    banner("UDP & DNS TESTS")
    for h in (whitelist, target):
        ok, addrs = resolve(h)
        if not ok:
            print(f"[SKIP] {h} resolution failed.")
            continue
        for fam, ip in addrs:
            if fam == socket.AF_INET6:
                print(f"[SKIP] UDP simple test skipping IPv6 for {ip}")
                continue
            print(f"[TEST] UDP packet to {ip}:53 (DNS) — check your DNS logs")
            succ, info = udp_send(ip, 53, payload=b"probe-"+random_label(6).encode())
            print(f"{'[OK]' if succ else '[FAIL]'} -> {info}")

            print(f"[TEST] UDP packet to {ip}:9999 (random UDP port)")
            succ, info = udp_send(ip, 9999, payload=b"probe-"+random_label(6).encode())
            print(f"{'[OK]' if succ else '[FAIL]'} -> {info}")

    # Try connecting to internal / link-local IPs (metadata & private ranges)
    banner("LOCAL & RFC1918 FILTER CHECKS (expected BLOCK)")
    private_targets = ["127.0.0.1", "169.254.169.254", "10.0.0.1", "172.16.0.1", "192.168.1.1"]
    for ip in private_targets:
        print(f"[TEST] TCP connect to {ip}:80")
        succ, info = tcp_connect(ip, 80)
        print(f"{'[OK]' if succ else '[BLOCKED/FAIL]'} -> {info}")

    # Try invoking curl/openssl if available
    banner("SUBPROCESS TOOLS (curl / openssl) if present")
    sp = test_subprocess_tools(target, whitelist)
    print("curl -vI result (truncated):")
    print(sp['curl_head']['stderr'][:2000])
    print("\nopenssl s_client output (truncated):")
    print(sp['openssl_s_client']['stdout'][:2000], sp['openssl_s_client']['stderr'][:2000])

    # Small DNS exfil style check (unique label) - send UDP query to given dns_server or to target's IP:53
    banner("DNS-EXFIL STYLE CHECK (small test) — observe your DNS logs/authoritative server")
    unique = random_label(10) + "." + target
    dns_dest = dns_server if dns_server else None
    if dns_dest:
        print(f"[TEST] UDP DNS query to server {dns_dest} for {unique}")
        ok, data = dns_query_udp(dns_dest, unique)
        print(f"{'[OK]' if ok else '[FAIL]'} -> {data}")
    else:
        # fallback: send to target's ip port 53
        ok, addrs = resolve(target)
        if ok and addrs:
            ip = addrs[0][1]
            print(f"[TEST] UDP DNS-like packet to {ip}:53 for {unique}")
            succ, info = udp_send(ip, 53, payload=b"exfil-"+unique.encode()[:100])
            print(f"{'[OK]' if succ else '[FAIL]'} -> {info}")
        else:
            print("[SKIP] No DNS server provided and target resolution failed; skipping DNS-exfil test")

    banner("SUMMARY & NEXT STEPS")
    print("Check your server logs for incoming connections from this sandbox (IPs will be the sandbox's egress IPs).")
    print("If connections to your whitelisted host succeed and to the non-whitelisted host fail, the egress policy is functioning.")
    print("If any unexpected connection succeeds (non-whitelisted host, local/internal IPs), collect logs and escalate.")
    print("If some TLS tests fail with 'certificate' or 'hostname mismatch', the proxy is likely validating TLS/SNI (good).")
    print("End of run.")
    print("="*80)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--whitelist", required=True, help="Whitelisted host (FQDN you expect to allow)")
    p.add_argument("--target", required=True, help="Non-whitelisted host (FQDN you expect to be blocked)")
    p.add_argument("--dns-server", required=False, help="Optional DNS server IP to send raw DNS queries to (useful to catch DNS exfil)")
    args = p.parse_args()
    try:
        perform_tests(args.whitelist, args.target, dns_server=args.dns_server)
    except Exception as e:
        print("Fatal error running tests:", e)
        traceback.print_exc()
        sys.exit(2)
