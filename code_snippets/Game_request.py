import json
import time
import random
import urllib.request
import urllib.error
import ssl
import gzip

_EMPTY = {
    "name": "",
    "appid": 0,
    "developers": [],
    "publishers": [],
    "short_desc": "",
    "release_date": "",
    "status": "",
    "message": "",
    "info": "",
    "price_currency": "",
    "price_initial": 0,
    "price_final": 0,
    "price_discount": 0,
    "has_price": False,
}


def main(appid: int) -> dict:
    time.sleep(random.uniform(2, 5))

    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=cn"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    https_handler = urllib.request.HTTPSHandler(context=ctx)
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(https_handler, proxy_handler)

    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            with opener.open(req, timeout=40) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                full = json.loads(raw.decode("utf-8"))
                game = full[str(appid)]
                if not game.get("success"):
                    return {**_EMPTY, "status": "error", "message": "游戏未找到"}
                d = game["data"]
                devs = d.get("developers") or []
                pubs = d.get("publishers") or []

                # 提取价格信息 (Steam 价格单位是"分"，除以100)
                price_info = d.get("price_overview") or {}
                currency = price_info.get("currency", "")
                initial = round(price_info.get("initial", 0) / 100, 2)
                final = round(price_info.get("final", 0) / 100, 2)
                discount = price_info.get("discount_percent", 0)

                info = (
                    f"游戏名: {d.get('name', '')}\n"
                    f"Steam ID: {d.get('steam_appid', '')}\n"
                    f"开发商: {', '.join(devs)}\n"
                    f"发行商: {', '.join(pubs)}\n"
                    f"发售日期: {d.get('release_date', {}).get('date', '')}\n"
                    f"价格: {currency} {final} (原价 {initial}) 折扣 {discount}%\n"
                    f"简介: {d.get('short_description', '')}"
                )
                return {
                    "name": d.get("name"),
                    "appid": d.get("steam_appid"),
                    "developers": devs,
                    "publishers": pubs,
                    "short_desc": d.get("short_description"),
                    "release_date": d.get("release_date", {}).get("date"),
                    "status": "success",
                    "message": "",
                    "info": info,
                    "price_currency": currency,
                    "price_initial": initial,
                    "price_final": final,
                    "price_discount": discount,
                    "has_price": currency != "",
                }

        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(5)
                continue
            return {**_EMPTY, "status": "error", "message": f"HTTP {e.code}", "info": ""}
        except urllib.error.URLError as e:
            if attempt == 0:
                time.sleep(2)
                continue
            return {**_EMPTY, "status": "error", "message": f"网络不通: {e.reason}", "info": ""}
        except Exception as e:
            return {**_EMPTY, "status": "error", "message": f"{type(e).__name__}: {e}", "info": ""}

    return {**_EMPTY, "status": "error", "message": "重试后仍失败", "info": ""}