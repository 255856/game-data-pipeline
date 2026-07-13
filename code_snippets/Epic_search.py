import json
import urllib.request
import urllib.error
import ssl
import time


def main(last_run_date: str = "") -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(https_handler, proxy_handler)

    game_names = []
    error_msg = ""

    for retry in range(3):
        try:
            url ="https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.9",
            })
            with opener.open(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
                for game in elements:
                    name = game.get("title", "").strip()
                    if name and name not in game_names:
                        game_names.append(name)
                break
        except Exception as e:
            if retry < 2:
                time.sleep(3)
            else:
                error_msg = f"{type(e).__name__}: {e}"

    return {
        "game_names": game_names[:10],
        "count": len(game_names[:10]),
        "source": "epic_free",
        "error": error_msg,
    }