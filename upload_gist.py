#!/usr/bin/env python3
"""
safe_upload_gist.py

Safe, auditable proof-of-concept: upload ONE explicitly-named test file
to GitHub Gist using a personal access token you provide.

Usage:
  export GITHUB_TOKEN="ghp_..."
  python3 safe_upload_gist.py exfil_allowed.txt --public false

Caveats:
- Do NOT point this at '.' or upload arbitrary directories.
- The file must exist and contain only test data you created.
"""

import sys, os, json, argparse, requests

def is_safe_content(path):
    # simple guard: only allow small files and printable chars
    try:
        st = os.stat(path)
        if st.st_size == 0 or st.st_size > 20000:
            return False, f"size={st.st_size} not allowed"
        with open(path, "rb") as f:
            data = f.read()
        # require mostly printable ASCII (reject binary)
        try:
            txt = data.decode("utf-8")
        except Exception:
            return False, "not utf-8 text"

        return True, txt
    except Exception as e:
        return False, f"error reading: {e}"

def create_gist(token, filename, content, public=False, description="egress test"):
    url = "https://api.github.com/gists"
    headers = {
        "Authorization": f"token {token}",
        "User-Agent": "egress-probe-poc",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "description": description,
        "public": bool(public),
        "files": {
            os.path.basename(filename): {"content": content}
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    return r

def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", help="Explicit filename to upload (must exist in cwd)")
    p.add_argument("--public", action="store_true", help="Make gist public (default false)")
    args = p.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: set GITHUB_TOKEN env var (token must have gist scope).")
        sys.exit(1)

    if not os.path.isfile(args.file):
        print(f"ERROR: file not found: {args.file}")
        sys.exit(1)

    ok, result = is_safe_content(args.file)
    if not ok:
        print("Refusing to upload: safety check failed:", result)
        sys.exit(1)

    content = result
    print("File OK; size:", len(content))
    print("Uploading to GitHub Gist (private={})...".format(not args.public))
    try:
        r = create_gist(token, args.file, content, public=args.public)
        if r.status_code in (201,):
            j = r.json()
            print("SUCCESS: Gist created")
            print("URL:", j.get("html_url"))
            print("Raw file URL:", next(iter(j.get("files",{}).values())).get("raw_url"))
            print(json.dumps(j, indent=2))
            sys.exit(0)
        else:
            print("Gist API returned", r.status_code)
            try:
                print(r.json())
            except Exception:
                print(r.text)
            sys.exit(2)
    except Exception as e:
        print("Network/API error:", e)
        sys.exit(3)

if __name__ == "__main__":
    main()
