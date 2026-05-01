#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         YuviXAkshit TOOL v4.0 — ENCRYPT + DECRYPT           ║
║   16-Layer XOR · GZIP · B64 · REV · ROT13                   ║
║   Live GitHub Auth | 1-Min Sessions | Auto Terminal Wipe    ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, gzip, base64, hashlib, secrets, struct
import time, shutil, random, string, codecs, re
import urllib.request
from pathlib import Path

# ──────────────────────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────────────────────
LAYERS      = 16
HASH_FILE   = "hash.txt"
BACKUP_EXT  = ".yuviback"
SKIP_CONFIG = ["config.php", "hash.txt", ".htaccess"]
TARGET_EXTS = {".php", ".html", ".htm", ".phtml"}
AUTH_URL    = "https://raw.githubusercontent.com/AKMKFI8838/Raw/refs/heads/main/key.txt"
SESSION_DUR = 60 # 1 minute in seconds

# ──────────────────────────────────────────────────────────────
#  COLOURS
# ──────────────────────────────────────────────────────────────
R="\033[91m"; G="\033[92m"; Y="\033[93m"; C="\033[96m"
M="\033[95m"; W="\033[0m";  B="\033[1m";  DIM="\033[2m"

def ok(m):    print(f"  {G}[✓]{W} {m}")
def info(m):  print(f"  {C}[*]{W} {m}")
def warn(m):  print(f"  {Y}[!]{W} {m}")
def err(m):   print(f"  {R}[✗]{W} {m}")
def head(m):  print(f"\n{B}{C}{'─'*54}\n  {m}\n{'─'*54}{W}")
def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

# ──────────────────────────────────────────────────────────────
#  AUTHENTICATION
# ──────────────────────────────────────────────────────────────
def authenticate():
    clear_screen()
    head("AUTHENTICATION REQUIRED")
    info("Connecting to Auth Server...")
    try:
        req = urllib.request.Request(AUTH_URL)
        with urllib.request.urlopen(req, timeout=10) as response:
            valid_keys = response.read().decode('utf-8').splitlines()
    except Exception as e:
        err(f"Failed to connect to auth server: {e}")
        sys.exit(1)

    user_key = input(f"\n  {Y}Enter your access key: {W}").strip()
    
    if user_key in valid_keys and user_key != "":
        ok("Access Granted! Session valid for 1 minute.")
        time.sleep(1)
        return time.time()
    else:
        err("Invalid Key! Access Denied.")
        sys.exit(1)

# ──────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────
def rand_var(n=16):
    return random.choice(string.ascii_letters) + \
           ''.join(random.choices(string.ascii_letters + string.digits, k=n-1))

def cjk_junk(n=60):
    return ''.join(chr(random.randint(0x4e00,0x9fff)) for _ in range(n))

# ──────────────────────────────────────────────────────────────
#  KEY MANAGEMENT
# ──────────────────────────────────────────────────────────────
def generate_key(n=64): return secrets.token_bytes(n)

def save_key(key, run_dir):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    txt = (f"# YUVIXAKSHIT-ENC — MASTER KEY\n"
           f"# Generated : {ts}\n"
           f"# NEVER UPLOAD TO WEB\n\n"
           f"KEY_HEX   = {key.hex()}\n"
           f"KEY_B64   = {base64.b64encode(key).decode()}\n"
           f"KEY_SHA256= {hashlib.sha256(key).hexdigest()}\n"
           f"LAYERS    = {LAYERS}\n")
    path = os.path.join(run_dir, HASH_FILE)
    with open(path,"w") as f: f.write(txt)
    return path

def load_key(run_dir):
    path = os.path.join(run_dir, HASH_FILE)
    if not os.path.exists(path): return None
    with open(path) as f:
        for line in f:
            if line.startswith("KEY_HEX"):
                return bytes.fromhex(line.split("=",1)[1].strip())
    return None

# ──────────────────────────────────────────────────────────────
#  ENCRYPTION CORE
# ──────────────────────────────────────────────────────────────
def xor_enc(data: bytes, key: bytes) -> bytes:
    r = bytearray(len(data))
    kl = len(key)
    for i,b in enumerate(data): r[i] = b ^ key[i%kl]
    return struct.pack(">I", len(data)) + bytes(r)

def full_encrypt(data: bytes, key: bytes, layers: int) -> bytes:
    d = gzip.compress(data, compresslevel=9)
    for n in range(1, layers+1):
        k1 = hashlib.sha512(key + bytes([n]) + b"YuviA").digest()
        k2 = hashlib.sha512(key + bytes([n]) + b"YuviB").digest()
        d = xor_enc(d, k1)
        d = xor_enc(d, k2)
    d = base64.b64encode(d).decode('ascii')
    d = d[::-1]
    d = codecs.encode(d, 'rot_13')
    return d.encode('ascii')

# ──────────────────────────────────────────────────────────────
#  DECRYPTION CORE 
# ──────────────────────────────────────────────────────────────
def xor_dec_layer(data: bytes, key: bytes) -> bytes:
    if len(data) < 4: raise ValueError("Data too short")
    length = struct.unpack(">I", data[:4])[0]
    body   = data[4:]
    kl     = len(key)
    r      = bytearray(length)
    for i in range(length): r[i] = body[i] ^ key[i%kl]
    return bytes(r)

def full_decrypt(payload_str: str, key: bytes, layers: int) -> bytes:
    d = codecs.decode(payload_str.strip(), 'rot_13')
    d = d[::-1]
    d = base64.b64decode(d)
    for n in range(layers, 0, -1):
        k2 = hashlib.sha512(key + bytes([n]) + b"YuviB").digest()
        d  = xor_dec_layer(d, k2)
        k1 = hashlib.sha512(key + bytes([n]) + b"YuviA").digest()
        d  = xor_dec_layer(d, k1)
    return gzip.decompress(d)

# ──────────────────────────────────────────────────────────────
#  PHP STUB BUILDER (Dynamic Paths + No Comments)
# ──────────────────────────────────────────────────────────────
def build_stub(payload_str: str, key_hex: str, layers: int, is_php: bool, orig_path: str) -> str:
    v  = {k: rand_var() for k in [
        'rot','rev','b64','gz','hx','hash',
        'k','p','d','l','k1','k2','ln','out','i','jnk','kl',
        'ob'
    ]}

    junk = cjk_junk(60)

    stub = f"""<?php
@error_reporting(0);@ini_set('display_errors',0);@set_time_limit(0);@ini_set('memory_limit','512M');
${v['jnk']}="{junk}";
${v['rot']}='str_rot13';
${v['rev']}=${v['rot']}('fgeeri');
${v['b64']}=${v['rot']}('onfr64_qrpbqr');
${v['hx']}=${v['rot']}('urk2ova');
${v['hash']}=${v['rot']}('unfu');
if(!function_exists('gzdecode')){{function gzdecode($x){{return gzinflate(substr($x,10,-8));}}}}
${v['gz']}='gzdecode';
${v['k']}='{key_hex}';
${v['p']}=<<<'YUX'
{payload_str}
YUX;
${v['d']}=trim(${v['p']});
${v['d']}=${v['rot']}(${v['d']});
${v['d']}=${v['rev']}(${v['d']});
${v['d']}=${v['b64']}(${v['d']});
for(${v['l']}={layers};${v['l']}>=1;${v['l']}--){{
${v['k2']}=${v['hash']}('sha512',${v['hx']}(${v['k']}).chr(${v['l']}).'YuviB',true);
${v['ln']}=unpack('N',substr(${v['d']},0,4))[1];
${v['d']}=substr(${v['d']},4,${v['ln']});
${v['out']}='';${v['kl']}=strlen(${v['k2']});
for(${v['i']}=0;${v['i']}<${v['ln']};${v['i']}++){{${v['out']}.=${v['d']}[${v['i']}]^${v['k2']}[${v['i']}%${v['kl']}];}}
${v['k1']}=${v['hash']}('sha512',${v['hx']}(${v['k']}).chr(${v['l']}).'YuviA',true);
${v['ln']}=unpack('N',substr(${v['out']},0,4))[1];
${v['out']}=substr(${v['out']},4,${v['ln']});
${v['d']}='';${v['kl']}=strlen(${v['k1']});
for(${v['i']}=0;${v['i']}<${v['ln']};${v['i']}++){{${v['d']}.=${v['out']}[${v['i']}]^${v['k1']}[${v['i']}%${v['kl']}];}}
}}
${v['d']}=${v['gz']}(${v['d']});
${v['d']}="<?php define('__YUVI_FILE__', '".addslashes(__FILE__)."'); define('__YUVI_DIR__', '".addslashes(__DIR__)."'); ?>".${v['d']};
"""

    if is_php:
        stub += f"""ob_start();eval('?>'.${v['d']});${v['ob']}=ob_get_clean();if(${v['ob']}!=='')echo ${v['ob']};"""
    else:
        stub += f"""ob_start();eval('?>'.${v['d']});${v['ob']}=ob_get_clean();header('Content-Type:text/html;charset=UTF-8');if(${v['ob']}!=='')echo ${v['ob']};"""

    stub += f"""\nunset(${v['jnk']},${v['rot']},${v['rev']},${v['b64']},${v['gz']},${v['hx']},${v['hash']},${v['k']},${v['p']},${v['d']},${v['l']},${v['k1']},${v['k2']},${v['ln']},${v['out']},${v['i']},${v['kl']},${v['ob']});
"""
    return stub

# ──────────────────────────────────────────────────────────────
#  FILE PROCESSOR
# ──────────────────────────────────────────────────────────────
def encrypt_file(filepath: str, key: bytes) -> tuple[bool, str]:
    path = Path(filepath)
    ext  = path.suffix.lower()
    if ext not in TARGET_EXTS:
        return False, "skipped (ext)"
    try:
        with open(filepath,"rb") as f: source = f.read()
    except Exception as e:
        return False, f"read error: {e}"

    if b"eval('?>'" in source or b"YUX;" in source:
        return False, "already encrypted"
    if not source.strip():
        return False, "empty"

    payload     = full_encrypt(source, key, LAYERS)
    payload_str = payload.decode('ascii')
    is_php      = (ext == ".php" or ext == ".phtml")
    stub        = build_stub(payload_str, key.hex(), LAYERS, is_php, filepath)

    out_path    = filepath if is_php else str(path.with_suffix(".php"))
    backup_path = filepath + BACKUP_EXT
    shutil.copy2(filepath, backup_path)

    try:
        with open(out_path,"w",encoding="utf-8") as f: f.write(stub)
        os.chmod(out_path, 0o644)
        if not is_php and out_path != filepath:
            os.remove(filepath)
    except Exception as e:
        shutil.copy2(backup_path, filepath)
        return False, f"write error: {e}"

    return True, f"{len(source)}B → {os.path.getsize(out_path)}B"

# ──────────────────────────────────────────────────────────────
#  DECRYPT
# ──────────────────────────────────────────────────────────────
def decrypt_once(text: str):
    if "YUX" not in text or "eval('?>'" not in text:
        return None
    km = re.search(r"\$\w+\s*=\s*'([0-9a-fA-F]{128})'", text)
    pm = re.search(r"<<<'YUX'\r?\n(.*?)\r?\nYUX;", text, re.DOTALL)
    lm = re.search(r"for\(\$\w+=(\d+);\$\w+>=1;\$\w+--\)", text)
    if not km or not pm: return None
    key     = bytes.fromhex(km.group(1))
    payload = pm.group(1).strip()
    layers  = int(lm.group(1)) if lm else 16
    return full_decrypt(payload, key, layers)

def decrypt_file_inplace(filepath: str) -> tuple[bool, str]:
    try:
        with open(filepath,"rb") as f: raw = f.read()
    except Exception as e:
        return False, f"read error: {e}"

    passes  = 0
    content = raw
    while True:
        try: text = content.decode("utf-8", errors="replace")
        except Exception: break
        result = decrypt_once(text)
        if result is None: break
        content = result
        passes += 1
        if passes > 20: return False, "too many passes (>20)"

    if passes == 0:
        return False, "not encrypted (skipped)"

    try:
        with open(filepath,"wb") as f: f.write(content)
    except Exception as e:
        return False, f"write error: {e}"

    return True, f"{passes} pass(es) → {len(content)} bytes"

# ──────────────────────────────────────────────────────────────
#  SELF-TEST
# ──────────────────────────────────────────────────────────────
def self_test(key: bytes) -> bool:
    src = b"<?php echo 'YUVI TEST OK: '.(1+1); ?>"
    enc = full_encrypt(src, key, LAYERS)
    dec = full_decrypt(enc.decode('ascii'), key, LAYERS)
    if dec == src:
        ok(f"Self-test PASSED ✓  ({LAYERS}×2 layers verified)")
        return True
    err("Self-test FAILED — mismatch!")
    return False

# ──────────────────────────────────────────────────────────────
#  FILE COLLECTION & HTACCESS
# ──────────────────────────────────────────────────────────────
def collect_files(target_dir: str, skip_list: list) -> list:
    files = []
    me = os.path.abspath(__file__)
    skip_lower = [s.lower() for s in skip_list]
    for root, dirs, names in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in {"vendor","node_modules","__pycache__"}]
        for name in names:
            if name.lower() in skip_lower: continue
            if name.endswith(BACKUP_EXT): continue
            fp = os.path.abspath(os.path.join(root, name))
            if fp == me: continue
            if Path(name).suffix.lower() in TARGET_EXTS:
                files.append(fp)
    return sorted(files)

def write_htaccess(target_dir: str):
    block = """\n<FilesMatch "\\.yuviback$">
    Order deny,allow
    Deny from all
</FilesMatch>
<FilesMatch "hash\\.txt$">
    Order deny,allow
    Deny from all
</FilesMatch>
"""
    path = os.path.join(target_dir, ".htaccess")
    existing = open(path).read() if os.path.exists(path) else ""
    if "yuviback" not in existing:
        with open(path,"a") as f: f.write(block)
        ok(".htaccess security rules added")

# ──────────────────────────────────────────────────────────────
#  UI HELPERS & MENUS
# ──────────────────────────────────────────────────────────────
def banner(remaining_time):
    print(f"""
{C}{B}╔══════════════════════════════════════════════════════════════╗
║          YuviXAkshit TOOL v4.0 — All-in-One                  ║
║   [E] Encrypt  ·  [D] Decrypt  ·  [T] Self-Test  ·  [Q] Quit ║
╚══════════════════════════════════════════════════════════════╝{W}
  {DIM}Session expires in: {int(remaining_time)} seconds{W}""")

def ask(prompt, choices):
    while True:
        try:
            v = input(f"\n  {Y}{prompt}{W} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(); return 'q'
        if v in choices: return v
        warn(f"Enter one of: {', '.join(choices)}")

def confirm(prompt):
    return ask(f"{prompt} (yes/no):", {"yes","y","no","n"}) in ("yes","y")

def pause():
    input(f"\n  {C}Press Enter to return to menu...{W}")

# ──────────────────────────────────────────────────────────────
#  MAIN FLOWS
# ──────────────────────────────────────────────────────────────
def run_encrypt(target_dir):
    clear_screen()
    run_dir = os.getcwd()
    head("KEY SETUP")
    existing = load_key(run_dir)
    if existing:
        warn(f"Reusing existing key from {HASH_FILE}")
        key = existing
    else:
        key = generate_key(64)
        p   = save_key(key, run_dir)
        ok(f"New 512-bit key saved → {p}")

    head("SELF-TEST")
    if not self_test(key):
        err("Aborting."); pause(); return

    skip = list(SKIP_CONFIG)
    extra = input(f"\n  {Y}Extra file to skip (Enter = none): {W}").strip()
    if extra:
        skip.append(extra)
        ok(f"Added {extra!r} to skip list")

    head("SCAN")
    files = collect_files(target_dir, skip)
    if not files:
        warn("No target files found."); pause(); return

    info(f"Found {len(files)} file(s):")
    for f in files: print(f"    {G}→{W} {os.path.relpath(f, target_dir)}")

    if not confirm("\n  Proceed? Files will be REPLACED in-place."):
        warn("Aborted."); pause(); return

    head("ENCRYPTING")
    ok_n = skip_n = fail_n = 0
    t0 = time.time()
    for fp in files:
        rel = os.path.relpath(fp, target_dir)
        success, msg = encrypt_file(fp, key)
        if success:
            ok(f"{rel}  [{msg}]"); ok_n += 1
        elif "skip" in msg or "already" in msg or "empty" in msg:
            warn(f"{rel}  [{msg}]"); skip_n += 1
        else:
            err(f"{rel}  [{msg}]"); fail_n += 1

    write_htaccess(target_dir)

    head("SUMMARY")
    print(f"  {G}Encrypted : {ok_n}{W}")
    print(f"  {Y}Skipped   : {skip_n}{W}")
    print(f"  {R}Failed    : {fail_n}{W}")
    print(f"  Time      : {time.time()-t0:.2f}s")

    if ask("\n  Delete .yuviback backup files? (yes/no):", {"yes","y","no","n"}) in ("yes","y"):
        n = 0
        for root,_,names in os.walk(target_dir):
            for name in names:
                if name.endswith(BACKUP_EXT):
                    try: os.remove(os.path.join(root,name)); n+=1
                    except: pass
        ok(f"Deleted {n} backup(s)")
    else:
        info("Backups retained")
    pause()

def run_decrypt(target_dir):
    clear_screen()
    head("SCANNING FOR ENCRYPTED FILES")
    all_php = []
    for root,dirs,names in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in {"vendor","node_modules","__pycache__"}]
        for name in names:
            if Path(name).suffix.lower() in {".php",".phtml"}:
                all_php.append(os.path.join(root, name))

    stubs = []
    for fp in sorted(all_php):
        try:
            with open(fp,"r",encoding="utf-8",errors="replace") as f: peek = f.read(8192)
            if "YUX" in peek and "eval('?>'" in peek: stubs.append(fp)
        except: pass

    if not stubs:
        warn("No encrypted stubs found in this directory."); pause(); return

    info(f"Found {len(stubs)} encrypted file(s):")
    for f in stubs: print(f"    {G}→{W} {os.path.relpath(f, target_dir)}")

    if not confirm("\n  Replace all in-place with decrypted originals?"):
        warn("Aborted."); pause(); return

    head("DECRYPTING")
    ok_n = skip_n = fail_n = 0
    for fp in stubs:
        rel = os.path.relpath(fp, target_dir)
        print(f"\n  {B}──{W} {rel}")
        success, msg = decrypt_file_inplace(fp)
        if success:
            ok(msg); ok_n += 1
        elif "skipped" in msg:
            warn(msg); skip_n += 1
        else:
            err(msg); fail_n += 1

    head("SUMMARY")
    print(f"  {G}Decrypted : {ok_n}{W}")
    print(f"  {Y}Skipped   : {skip_n}{W}")
    print(f"  {R}Failed    : {fail_n}{W}")
    pause()

def main():
    if len(sys.argv) > 1: target_dir = os.path.abspath(sys.argv[1])
    else: target_dir = os.getcwd()

    if not os.path.isdir(target_dir):
        err(f"Not a directory: {target_dir}"); sys.exit(1)

    # Trigger Authentication Sequence
    session_start = authenticate()

    while True:
        clear_screen()
        time_elapsed = time.time() - session_start
        if time_elapsed > SESSION_DUR:
            err("SESSION EXPIRED. Please restart the script to authenticate again.")
            sys.exit(0)
            
        remaining = SESSION_DUR - time_elapsed
        banner(remaining)
        print(f"  {DIM}Directory : {target_dir}{W}")

        print(f"""
  {B}┌─────────────────────────────┐
  │  {G}[E]{W}{B} Encrypt PHP files       │
  │  {C}[D]{W}{B} Decrypt PHP files       │
  │  {Y}[T]{W}{B} Run self-test           │
  │  {R}[Q]{W}{B} Quit                    │
  └─────────────────────────────┘{W}""")

        choice = ask("Choose option [E/D/T/Q]:", {"e","d","t","q"})

        if choice == "e": run_encrypt(target_dir)
        elif choice == "d": run_decrypt(target_dir)
        elif choice == "t":
            clear_screen()
            head("SELF-TEST")
            self_test(generate_key(64))
            pause()
        elif choice == "q":
            clear_screen()
            print(f"\n  {C}Bye!{W}\n")
            break

if __name__ == "__main__":
    main()
