import json
import urllib.request
import ssl
from datetime import datetime, timezone, timedelta


def main(summary: str = "", steam_games: str = "", epic_games: str = "", webhook_key: str =
"31aeb7ca-7aed-4767-8826-9cba80664379", **_kwargs) -> dict:
    if not webhook_key:
        return {"status": "skipped", "message": "未配置 webhook_key"}

    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"

    all_games = []
    for src in [steam_games, epic_games]:
        if src:
            try:
                if isinstance(src, str):
                    names = json.loads(src)
                else:
                    names = src
                all_games.extend(names)
            except:
                pass

    if all_games:
        games_lines = "\n".join(f"{i}. {g}" for i, g in enumerate(all_games[:30], 1))
    else:
        games_lines = "无"

    push_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

    content = (
        f"## 游戏数据同步日报\n"
        f"**推送时间**：{push_time}\n"
        f"{summary}\n"
        f"\n**本次游戏**：\n"
        f"{games_lines}"
    )

    body = {"msgtype": "markdown", "markdown": {"content": content}}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(handler)

    try:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with opener.open(req, timeout=15) as resp:
            resp_body = resp.read().decode("utf-8")
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": resp_body}