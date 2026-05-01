#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         YuviXAkshit PRO ENGINE v6.0 — SECURE SUITE           ║
║   16-Layer Omni Matrix | Dynamic UI | Cache-Bust Auth        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, gzip, base64, hashlib, secrets, struct
import time, shutil, random, string, codecs, re
import urllib.request, platform
from pathlib import Path

# ──────────────────────────────────────────────────────────────
#  SYSTEM CONFIGURATION
# ──────────────────────────────────────────────────────────────
LAYERS      = 16
HASH_FILE   = "hash.txt"
BACKUP_EXT  = ".yuviback"
SKIP_CONFIG = ["config.php", "hash.txt", ".htaccess"]
TARGET_EXTS = {".php", ".html", ".htm", ".phtml"}
AUTH_URL    = "https://raw.githubusercontent.com/AKMKFI8838/Raw/refs/heads/main/key.txt"
SESSION_DUR = 60 # 1 minute in seconds

# ──────────────────────────────────────────────────────────────
#  PREMIUM ANSI COLORS & UI STYLING
# ──────────────────────────────────────────────────────────────
class C:
    R = "\033[38;5;196m"  # Red
    G = "\033[38;5;46m"   # Neon Green
    Y = "\033[38;5;226m"  # Yellow
    C = "\033[38;5;51m"   # Cyan
    M = "\033[38;5;201m"  # Magenta
    D = "\033[38;5;240m"  # Dark Gray
    W = "\033[0m"         # Reset
    B = "\033[1m"         # Bold

def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

def sys_print(prefix, color, msg):
    print(f"  {C.D}[{color}{C.B}{prefix}{C.D}]{C.W} {msg}")

def ok(m):   sys_print("✓", C.G, m)
def info(m): sys_print("i", C.C, m)
def warn(m): sys_print("!", C.Y, m)
def err(m):  sys_print("✗", C.R, m)
def pause(): input(f"\n  {C.C}Press [ENTER] to return to dashboard...{C.W}")

def progress_bar(iteration, total, prefix='', length=40):
    """Dynamic professional progress bar"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    sys.stdout.write(f'\r  {C.C}{prefix} {C.D}|{C.G}{bar}{C.D}| {C.C}{percent}%{C.W} ')
    sys.stdout.flush()
    if iteration == total: print()

def dashboard_header(remaining_time, target_dir):
    """Draws a premium terminal dashboard"""
    clear_screen()
    sys_os = platform.system()
    sys_arch = platform.machine()
    
    print(f"""{C.C}{C.B}
  ╔═════════════════════════════════════════════════════════════════╗
  ║  {C.W}Y U V I X A K S H I T   P R O   E N G I N E   v 6 . 0{C.C}          ║
  ╠═════════════════════════════════════════════════════════════════╣
  ║  {C.D}SYSTEM:{C.W} {sys_os} ({sys_arch})                  {C.D}MODE:{C.W} 16-Layer Omni    {C.C}║
  ║  {C.D}TARGET:{C.W} {target_dir[:36]:<36} {C.D}TIME:{C.W} {int(remaining_time):02d}s Session   {C.C}║
  ╚═════════════════════════════════════════════════════════════════╝{C.W}""")

# ──────────────────────────────────────────────────────────────
#  LIVE AUTHENTICATION (CACHE-BUSTING)
# ──────────────────────────────────────────────────────────────
def authenticate():
    clear_screen()
    print(f"\n{C.C}{C.B}  [ YUVI SECURITY GATEWAY ]{C.W}\n")
    info("Establishing secure connection to Auth Server...")
    try:
        url = f"{AUTH_URL}?t={int(time.time())}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            valid_keys = [line.strip() for line in response.read().decode('utf-8').splitlines() if line.strip()]
    except Exception as e:
        err(f"Server unreachable: {e}")
        sys.exit(1)

    user_key = input(f"\n  {C.Y}Enter Access Protocol Key: {C.W}").strip()
    
    if user_key in valid_keys:
        ok("Signature Verified. Access Granted.")
        time.sleep(1)
        return time.time()
    else:
        err("Invalid Signature. Connection Terminated.")
        sys.exit(1)

# ──────────────────────────────────────────────────────────────
#  HELPERS & KEY MANAGEMENT
# ──────────────────────────────────────────────────────────────
def rand_var(n=16):
    return random.choice(string.ascii_letters) + ''.join(random.choices(string.ascii_letters + string.digits, k=n-1))

def cjk_junk(n=60):
    return ''.join(chr(random.randint(0x4e00,0x9fff)) for _ in range(n))

def generate_key(n=64): return secrets.token_bytes(n)

def save_key(key, run_dir):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    txt = (f"# YUVIXAKSHIT PRO — MASTER KEY\n# Generated : {ts}\n"
           f"KEY_HEX   = {key.hex()}\nLAYERS    = {LAYERS}\n")
    path = os.path.join(run_dir, HASH_FILE)
    with open(path,"w") as f: f.write(txt)
    return path

def load_key(run_dir):
    path = os.path.join(run_dir, HASH_FILE)
    if not os.path.exists(path): return None
    with open(path) as f:
        for line in f:
            if line.startswith("KEY_HEX"): return bytes.fromhex(line.split("=",1)[1].strip())
    return None

# ──────────────────────────────────────────────────────────────
#  CORE CRYPTOGRAPHY
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
    d = base64.b64encode(d).decode('ascii')[::-1]
    return codecs.encode(d, 'rot_13').encode('ascii')

def xor_dec_layer(data: bytes, key: bytes) -> bytes:
    if len(data) < 4: raise ValueError("Data too short")
    length = struct.unpack(">I", data[:4])[0]
    body, kl, r = data[4:], len(key), bytearray(length)
    for i in range(length): r[i] = body[i] ^ key[i%kl]
    return bytes(r)

def full_decrypt(payload_str: str, key: bytes, layers: int) -> bytes:
    d = base64.b64decode(codecs.decode(payload_str.strip(), 'rot_13')[::-1])
    for n in range(layers, 0, -1):
        k2 = hashlib.sha512(key + bytes([n]) + b"YuviB").digest()
        d  = xor_dec_layer(d, k2)
        k1 = hashlib.sha512(key + bytes([n]) + b"YuviA").digest()
        d  = xor_dec_layer(d, k1)
    return gzip.decompress(d)

# ──────────────────────────────────────────────────────────────
#  PHP STUB BUILDER (Fully Dynamic & Silent)
# ──────────────────────────────────────────────────────────────
def build_stub(payload_str: str, key_hex: str, layers: int, is_php: bool) -> str:
    v = {k: rand_var() for k in ['rot','rev','b64','gz','hx','hash','k','p','d','l','k1','k2','ln','out','i','jnk','kl','ob']}
    junk = cjk_junk(60)

    stub = f"""<?php
@error_reporting(0);@ini_set('display_errors',0);@set_time_limit(0);@ini_set('memory_limit','512M');
${v['jnk']}="{junk}";${v['rot']}='str_rot13';${v['rev']}=${v['rot']}('fgeeri');${v['b64']}=${v['rot']}('onfr64_qrpbqr');
${v['hx']}=${v['rot']}('urk2ova');${v['hash']}=${v['rot']}('unfu');
if(!function_exists('gzdecode')){{function gzdecode($x){{return gzinflate(substr($x,10,-8));}}}}
${v['gz']}='gzdecode';${v['k']}='{key_hex}';
${v['p']}=<<<'YUX'
{payload_str}
YUX;
${v['d']}=${v['b64']}(${v['rev']}(${v['rot']}(trim(${v['p']}막))));
for(${v['l']}={layers};${v['l']}>=1;${v['l']}--){{
${v['k2']}=${v['hash']}('sha512',${v['hx']}(${v['k']}).chr(${v['l']}).'YuviB',true);
${v['ln']}=unpack('N',substr(${v['d']},0,4))[1];${v['d']}=substr(${v['d']},4,${v['ln']});
${v['out']}='';${v['kl']}=strlen(${v['k2']});
for(${v['i']}=0;${v['i']}<${v['ln']};${v['i']}++){{${v['out']}.=${v['d']}[${v['i']}]^${v['k2']}[${v['i']}%${v['kl']}];}}
${v['k1']}=${v['hash']}('sha512',${v['hx']}(${v['k']}).chr(${v['l']}).'YuviA',true);
${v['ln']}=unpack('N',substr(${v['out']},0,4))[1];${v['out']}=substr(${v['out']},4,${v['ln']});
${v['d']}='';${v['kl']}=strlen(${v['k1']});
for(${v['i']}=0;${v['i']}<${v['ln']};${v['i']}++){{${v['d']}.=${v['out']}[${v['i']}]^${v['k1']}[${v['i']}%${v['kl']}];}}
}}
${v['d']}=${v['gz']}(${v['d']});
${v['d']}="<?php define('__YUVI_FILE__', '".addslashes(__FILE__)."'); define('__YUVI_DIR__', '".addslashes(__DIR__)."'); ?>".${v['d']};
"""
    stub = stub.replace('막', '') # Fix string trim issue visually
    if is_php:
        stub += f"ob_start();eval('?>'.${v['d']});${v['ob']}=ob_get_clean();if(${v['ob']}!=='')echo ${v['ob']};"
    else:
        stub += f"ob_start();eval('?>'.${v['d']});${v['ob']}=ob_get_clean();header('Content-Type:text/html;charset=UTF-8');if(${v['ob']}!=='')echo ${v['ob']};"
    stub += f"\nunset(${v['jnk']},${v['rot']},${v['rev']},${v['b64']},${v['gz']},${v['hx']},${v['hash']},${v['k']},${v['p']},${v['d']},${v['l']},${v['k1']},${v['k2']},${v['ln']},${v['out']},${v['i']},${v['kl']},${v['ob']});\n"
    return stub

# ──────────────────────────────────────────────────────────────
#  FILE PROCESSORS
# ──────────────────────────────────────────────────────────────
def collect_files(target_dir: str, skip_list: list) -> list:
    files = []
    try: me = os.path.abspath(__file__)
    except NameError: me = "" 
    skip_lower = [s.lower() for s in skip_list]
    for root, dirs, names in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in {"vendor","node_modules","__pycache__"}]
        for name in names:
            if name.lower() in skip_lower or name.endswith(BACKUP_EXT): continue
            fp = os.path.abspath(os.path.join(root, name))
            if me and fp == me: continue
            if Path(name).suffix.lower() in TARGET_EXTS: files.append(fp)
    return sorted(files)

def write_htaccess(target_dir: str):
    block = "\n<FilesMatch \"\\.yuviback$\">\nOrder deny,allow\nDeny from all\n</FilesMatch>\n<FilesMatch \"hash\\.txt$\">\nOrder deny,allow\nDeny from all\n</FilesMatch>\n"
    path = os.path.join(target_dir, ".htaccess")
    existing = open(path).read() if os.path.exists(path) else ""
    if "yuviback" not in existing:
        with open(path,"a") as f: f.write(block)

def self_test(key: bytes) -> bool:
    src = b"<?php echo 'YUVI TEST OK'; ?>"
    dec = full_decrypt(full_encrypt(src, key, LAYERS).decode('ascii'), key, LAYERS)
    if dec == src:
        ok(f"Engine Integrity Verified ({LAYERS}x2 Matrix)")
        return True
    err("Engine Integrity Compromised!")
    return False

# ──────────────────────────────────────────────────────────────
#  OPERATIONS
# ──────────────────────────────────────────────────────────────
def run_encrypt(target_dir):
    print(f"\n  {C.B}── INITIALIZING ENCRYPTION PROTOCOL ──{C.W}")
    run_dir = os.getcwd()
    key = load_key(run_dir)
    if key: info(f"Loaded existing Master Key")
    else:
        key = generate_key(64)
        save_key(key, run_dir)
        ok(f"Generated new 512-bit Master Key")

    if not self_test(key): pause(); return

    skip = list(SKIP_CONFIG)
    extra = input(f"\n  {C.Y}Exclude specific file? (Enter = none): {C.W}").strip()
    if extra: skip.append(extra)

    files = collect_files(target_dir, skip)
    if not files: warn("No valid targets found."); pause(); return

    info(f"Targeting {len(files)} files for deployment.")
    if input(f"  {C.R}Deploy Payload? (y/n): {C.W}").strip().lower() not in ('y','yes'): return

    print()
    ok_n = skip_n = fail_n = 0
    total = len(files)
    
    for i, fp in enumerate(files):
        progress_bar(i + 1, total, prefix='Encrypting:')
        ext = Path(fp).suffix.lower()
        try:
            with open(fp,"rb") as f: src = f.read()
            if b"eval('?>'" in src or b"YUX;" in src: skip_n += 1; continue
            if not src.strip(): skip_n += 1; continue
            
            payload = full_encrypt(src, key, LAYERS).decode('ascii')
            is_php = (ext in [".php", ".phtml"])
            stub = build_stub(payload, key.hex(), LAYERS, is_php)
            
            out_path = fp if is_php else str(Path(fp).with_suffix(".php"))
            shutil.copy2(fp, fp + BACKUP_EXT)
            
            with open(out_path,"w",encoding="utf-8") as f: f.write(stub)
            os.chmod(out_path, 0o644)
            if not is_php and out_path != fp: os.remove(fp)
            ok_n += 1
        except Exception: fail_n += 1

    write_htaccess(target_dir)
    print(f"\n  {C.G}SUCCESS: {ok_n} {C.D}|{C.Y} SKIPPED: {skip_n} {C.D}|{C.R} FAILED: {fail_n}{C.W}")
    
    if input(f"\n  {C.C}Purge .yuviback backups? (y/n): {C.W}").strip().lower() in ('y','yes'):
        n = sum(1 for r,_,f in os.walk(target_dir) for x in f if x.endswith(BACKUP_EXT) and not os.remove(os.path.join(r,x)))
        ok(f"Purged {n} backup files.")
    pause()

def run_decrypt(target_dir):
    print(f"\n  {C.B}── INITIALIZING DECRYPTION PROTOCOL ──{C.W}")
    stubs = []
    for root,_,names in os.walk(target_dir):
        for name in [n for n in names if n.endswith(('.php','.phtml'))]:
            fp = os.path.join(root, name)
            try:
                with open(fp,"r",encoding="utf-8",errors="replace") as f: peek = f.read(8192)
                if "YUX" in peek and "eval('?>'" in peek: stubs.append(fp)
            except: pass

    if not stubs: warn("No encrypted payloads found."); pause(); return
    info(f"Detected {len(stubs)} encrypted files.")
    if input(f"  {C.R}Reverse Encryption? (y/n): {C.W}").strip().lower() not in ('y','yes'): return

    print()
    ok_n = fail_n = 0
    total = len(stubs)
    
    for i, fp in enumerate(stubs):
        progress_bar(i + 1, total, prefix='Decrypting:')
        try:
            with open(fp,"rb") as f: content = f.read().decode("utf-8", errors="replace")
            km = re.search(r"\$\w+\s*=\s*'([0-9a-fA-F]{128})'", content)
            pm = re.search(r"<<<'YUX'\r?\n(.*?)\r?\nYUX;", content, re.DOTALL)
            if not km or not pm: fail_n += 1; continue
            
            dec = full_decrypt(pm.group(1).strip(), bytes.fromhex(km.group(1)), LAYERS)
            with open(fp,"wb") as f: f.write(dec)
            ok_n += 1
        except Exception: fail_n += 1

    print(f"\n  {C.G}RECOVERED: {ok_n} {C.D}|{C.R} FAILED: {fail_n}{C.W}")
    pause()

def run_emergency_restore(target_dir):
    print(f"\n  {C.B}── EMERGENCY BACKUP RESTORE ──{C.W}")
    backups = []
    for root,_,names in os.walk(target_dir):
        for name in names:
            if name.endswith(BACKUP_EXT): backups.append(os.path.join(root, name))
            
    if not backups: warn("No .yuviback files found."); pause(); return
    
    info(f"Found {len(backups)} backup files.")
    if input(f"  {C.Y}Restore original files and overwrite current? (y/n): {C.W}").strip().lower() in ('y','yes'):
        for i, bp in enumerate(backups):
            progress_bar(i + 1, len(backups), prefix='Restoring:')
            orig_path = bp.replace(BACKUP_EXT, "")
            shutil.move(bp, orig_path)
        print(f"\n  {C.G}SYSTEM RESTORED SUCCESSFULLY.{C.W}")
    pause()

# ──────────────────────────────────────────────────────────────
#  MAIN LOOP
# ──────────────────────────────────────────────────────────────
def main():
    target_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    if not os.path.isdir(target_dir): err("Invalid directory."); sys.exit(1)

    session_start = authenticate()

    while True:
        time_elapsed = time.time() - session_start
        if time_elapsed > SESSION_DUR:
            clear_screen()
            warn("SESSION EXPIRED. Re-authenticating...")
            time.sleep(1)
            session_start = authenticate()
            continue
            
        dashboard_header(SESSION_DUR - time_elapsed, target_dir)

        print(f"""
    {C.G}[ 1 ]{C.W} Deploy Encryption Matrix
    {C.C}[ 2 ]{C.W} Reverse Decryption Process
    {C.Y}[ 3 ]{C.W} Emergency Backup Restore
    {C.D}[ 0 ]{C.W} Terminate Session
        """)

        choice = input(f"  {C.B}Select Operation (0-3):{C.W} ").strip()

        if choice == "1": run_encrypt(target_dir)
        elif choice == "2": run_decrypt(target_dir)
        elif choice == "3": run_emergency_restore(target_dir)
        elif choice == "0":
            clear_screen()
            print(f"\n  {C.C}Session Terminated. Goodbye.{C.W}\n")
            break

if __name__ == "__main__":
    main()
