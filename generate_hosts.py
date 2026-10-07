import os
import re
import socket
import urllib.parse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import requests
from fake_useragent import UserAgent

# 1. Danh sách nguồn Blocklist
SOURCES = [
    "https://adaway.org/hosts.txt",
    "https://gitlab.com/andryou/block/raw/master/chibi",
    "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext",
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "https://raw.githubusercontent.com/r-a-y/mobile-hosts/master/AdguardDNS.txt",
    "https://raw.githubusercontent.com/Turtlecute33/adblocktest/refs/heads/master/src/d3host.txt",
    "https://www.github.developerdan.com/hosts/lists/ads-and-tracking-extended.txt",
    "https://raw.githubusercontent.com/soctrungkien/1HzH9Axaj/refs/heads/main/uploads/blocklist------.txt",
    "https://raw.githubusercontent.com/soctrungkien/1HzH9Axaj/main/uploads/bloxkhosslt"
]

# REGEX Regex kiểm tra Domain hợp lệ
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

# Khởi tạo Fake UserAgent
try:
    ua = UserAgent()
except Exception:
    ua = None


def get_random_user_agent() -> str:
    """Tạo User-Agent ngẫu nhiên chân thực."""
    if ua:
        try:
            return ua.random
        except Exception:
            pass
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def get_proxies() -> dict | None:
    """Đọc cấu hình Proxy từ biến môi trường (HTTP, HTTPS, SOCKS5)."""
    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("ALL_PROXY")
    if proxy_url:
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    return None


def is_private_ip(ip_str: str) -> bool:
    """Kiểm tra IP có thuộc Private/Loopback (Chống SSRF)."""
    try:
        # IPv4 Check
        parts = list(map(int, ip_str.split('.')))
        if len(parts) == 4:
            a, b = parts[0], parts[1]
            if a in (0, 10, 127):
                return True
            if a == 100 and 64 <= b <= 127:
                return True
            if a == 169 and b == 254:
                return True
            if a == 172 and 16 <= b <= 31:
                return True
            if a == 192 and b == 168:
                return True
            return False
    except ValueError:
        pass

    # IPv6 Check
    low_ip = ip_str.lower().split('%')[0]
    if low_ip in ("::", "::1") or any(low_ip.startswith(prefix) for prefix in ("fc", "fd", "fe8", "fe9", "fea", "feb")):
        return True

    return False


def is_valid_domain(domain: str) -> bool:
    """Xác minh hostname hợp lệ và không nằm trong blacklist hệ thống."""
    if not domain:
        return False
    domain = domain.rstrip(".").strip().lower()

    # Chặn domain nội bộ / local
    if domain in ("localhost", "metadata.google.internal") or domain.endswith((".localhost", ".local", ".internal")):
        return False

    return bool(DOMAIN_REGEX.match(domain))


def extract_domain_from_line(line: str) -> str | None:
    """Parse linh hoạt các định dạng: Hosts, AdBlock Plus (||domain^), Domain thuần."""
    line = line.strip()

    if not line or line.startswith(("#", "!", "[")) or "##" in line or "#@#" in line:
        return None

    # Loại bỏ comment cuối dòng
    for sep in ("#", "!"):
        if sep in line:
            line = line.split(sep)[0].strip()

    if not line:
        return None

    # 1. Dạng AdGuard/uBlock Rules: ||example.com^
    if line.startswith("||"):
        domain = line[2:]
        if "/" in domain:
            return None
        for char in ("^", "$", ":"):
            if char in domain:
                domain = domain.split(char)[0]
        domain = domain.strip().lower()
        return domain if is_valid_domain(domain) else None

    # 2. Dạng Standard Hosts: 127.0.0.1 domain.com hoặc 0.0.0.0 domain.com
    parts = line.split()
    if len(parts) >= 2:
        ip, domain = parts[0], parts[1]
        if ip in ("127.0.0.1", "0.0.0.0", "::1") and is_valid_domain(domain):
            return domain.lower()

    # 3. Dạng danh sách Domain thuần
    if len(parts) == 1 and is_valid_domain(parts[0]):
        return parts[0].lower()

    return None


def fetch_source(url: str) -> str | None:
    """Tải dữ liệu từng nguồn với Retry, Custom User-Agent & Proxy."""
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    proxies = get_proxies()

    # Kiểm tra hostname chống SSRF trước khi request
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        if hostname:
            resolved_ip = socket.gethostbyname(hostname)
            if is_private_ip(resolved_ip):
                print(f"🚫 [SSRF BLOCKED] Hostname {hostname} giải mã ra Private IP: {resolved_ip}")
                return None
    except Exception:
        pass

    try:
        res = requests.get(
            url,
            timeout=20,
            headers=headers,
            proxies=proxies,
            allow_redirects=True
        )
        if res.status_code == 200 and res.text.strip():
            print(f"✅ [FETCHED OK] {len(res.text):,} bytes | {url}")
            return res.text
        print(f"⚠️ [HTTP {res.status_code}] {url}")
    except Exception as e:
        print(f"❌ [FETCH ERROR] {url} | {e}")
    return None


def main():
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    proxies = get_proxies()
    if proxies:
        print(f"🌐 Running with Proxy: {proxies['https']}")
    else:
        print("🌐 Direct Connection (No Proxy)")

    print(f"🚀 Tải dữ liệu song song từ {len(SOURCES)} nguồn...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_source, SOURCES))

    raw_contents = [r for r in results if r]
    print(f"📊 Thành công: {len(raw_contents)}/{len(SOURCES)} nguồn.")

    print("🔄 Đang xử lý, lọc trùng và tối ưu hóa danh sách domain...")
    unique_domains = set()
    for content in raw_contents:
        for line in content.splitlines():
            domain = extract_domain_from_line(line)
            if domain:
                unique_domains.add(domain)

    total_domains = len(unique_domains)
    print(f"✨ Tổng domain sạch thu thập được: {total_domains:,}")

    # Build định dạng Hosts File chuẩn
    hosts_header = (
        f"# Automatic Generate Blocklist\n"
        f"# Updated: {created_at}\n"
        f"# Total Blocked Domains: {total_domains:,}\n"
    )

    output_filename = "hosts"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(hosts_header)
        for domain in sorted(unique_domains):
            f.write(f"0.0.0.0 {domain}\n")

    print(f"🎉 Đã lưu file hosts thành công: {os.path.abspath(output_filename)}")


if __name__ == "__main__":
    main()
