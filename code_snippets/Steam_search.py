import json
import urllib.request
import urllib.error
import ssl
import gzip
import re
import time
import xml.etree.ElementTree as ET


def main(last_run_date: str = "") -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(https_handler, proxy_handler)
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    game_names = []
    sources = []
    error_msg = ""

    # 来源1: Steam RSS 新品 (最稳定, 3次重试, 45s超时)
    for retry in range(3):
        try:
            rss_headers = {**base_headers, "Accept": "application/xml, text/xml, */*"}
            req = urllib.request.Request(
                "https://store.steampowered.com/feeds/newreleases.xml?cc=cn",
                headers=rss_headers
            )
            with opener.open(req, timeout=45) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                content = raw.decode("utf-8", errors="ignore")
                root = ET.fromstring(content)
                for item in root.findall(".//item"):
                    title_el = item.find("title")
                    desc_el = item.find("description")
                    title_text = title_el.text if title_el is not None else ""
                    desc_text = desc_el.text if desc_el is not None else ""
                    appid_m = re.search(r"/app/(\d+)/", desc_text)
                    name = title_text
                    for prefix in ["Now Available on Steam - ", "Now Available - "]:
                        if name.startswith(prefix):
                            name = name[len(prefix):]
                    name = re.sub(r", \d+% off!$", "", name).strip()
                    if "DLC Available" in title_text or "Soundtrack" in title_text:
                        continue
                    if appid_m and name and name not in game_names:
                        game_names.append(name)
                if game_names:
                    sources.append("steam_rss")
                    break
        except Exception as e:
            if retry < 2:
                time.sleep(3)
            else:
                error_msg += f"rss: {type(e).__name__}; "

    time.sleep(1)

    # 来源2: Steam 热门新品 HTML
    try:
        html_headers = {**base_headers, "Accept": "text/html,application/xhtml+xml"}
        req = urllib.request.Request(
            "https://store.steampowered.com/search/?filter=popularnew&cc=cn&ndl=1",
            headers=html_headers
        )
        with opener.open(req, timeout=15) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            html = raw.decode("utf-8", errors="ignore")
            names = re.findall(r'<span class="title">([^<]+)</span>', html)
            for name in names:
                name = name.strip()
                if name and name not in game_names:
                    game_names.append(name)
            sources.append("steam_popular_new")
    except Exception as e:
        error_msg += f"popular: {type(e).__name__}; "

    time.sleep(1)

    # 来源3: Steam Featured API
    try:
        api_headers = {**base_headers, "Accept": "application/json"}
        req = urllib.request.Request(
            "https://store.steampowered.com/api/featuredcategories?cc=cn",
            headers=api_headers
        )
        with opener.open(req, timeout=15) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            data = json.loads(raw.decode("utf-8"))
            for category in ["new_releases", "top_sellers", "specials", "coming_soon"]:
                items = data.get(category, {}).get("items", [])
                for item in items[:3]:
                    name = item.get("name", "").strip()
                    if name and name not in game_names:
                        game_names.append(name)
            sources.append("steam_featured")
    except Exception as e:
        error_msg += f"featured: {type(e).__name__}; "

    # 来源4: Steam 即将推出 HTML
    try:
        html_headers = {**base_headers, "Accept": "text/html,application/xhtml+xml"}
        req = urllib.request.Request(
            "https://store.steampowered.com/search/?filter=comingsoon&cc=cn&ndl=1",
            headers=html_headers
        )
        with opener.open(req, timeout=15) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            html = raw.decode("utf-8", errors="ignore")
            names = re.findall(r'<span class="title">([^<]+)</span>', html)
            for name in names[:15]:
                name = name.strip()
                if name and name not in game_names:
                    game_names.append(name)
            sources.append("steam_coming_soon")
    except Exception as e:
        error_msg += f"coming: {type(e).__name__}; "

    game_names = game_names[:20]

    return {
        "game_names": game_names,
        "count": len(game_names),
        "source": "steam_" + "+".join(sources) if sources else "steam_none",
        "error": error_msg,
    }