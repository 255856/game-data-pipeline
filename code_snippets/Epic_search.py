import json
import urllib.request
import urllib.error
import ssl


def main(last_run_date: str = "") -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(https_handler, proxy_handler)

    game_names = []
    error_msg = ""

    try:
        url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0"
        })
        with opener.open(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
            for game in elements:
                name = game.get("title", "").strip()
                if name and name not in game_names:
                    game_names.append(name)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"

    return {
        "game_names": game_names[:10],
        "count": len(game_names[:10]),
        "source": "epic_free",
        "error": error_msg,
    }