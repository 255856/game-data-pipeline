import json
import re
from datetime import datetime, timezone, timedelta


def main(steam_count=None, steam_source: str = "", steam_sql: str = "",
         epic_count=None, epic_source: str = "", epic_sql: str = "",
         steam_prices_sql: str = "", epic_prices_sql: str = "") -> dict:
    now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

    steam_count = steam_count or 0
    epic_count = epic_count or 0

    def get_affected(sql_result):
        if not sql_result:
            return 0
        try:
            text = ""
            if isinstance(sql_result, str):
                try:
                    sr = json.loads(sql_result)
                    text = sr.get("text", "")
                except:
                    text = sql_result
            else:
                text = sql_result.get("text", "")
            m = re.search(r"Affected rows:\s*(\d+)", text)
            return int(m.group(1)) if m else 0
        except:
            return 0

    steam_games_affected = get_affected(steam_sql)
    steam_prices_affected = get_affected(steam_prices_sql)
    epic_games_affected = get_affected(epic_sql)
    epic_prices_affected = get_affected(epic_prices_sql)

    steam_total = steam_games_affected + steam_prices_affected
    epic_total = epic_games_affected + epic_prices_affected
    total_discovery = steam_count + epic_count
    total_affected = steam_total + epic_total

    sources = []
    if steam_count > 0:
        sources.append(steam_source)
    if epic_count > 0:
        sources.append(epic_source)

    html = f"""
<h2>游戏数据同步日报</h2>
<table border='1' style='border-collapse:collapse;width:500px'>
  <tr><td>执行时间</td><td>{now}</td></tr>
  <tr><td>数据来源</td><td>{', '.join(sources) if sources else '无'}</td></tr>
  <tr><td>Steam</td><td>发现 {steam_count} 款 / 游戏入库 {steam_games_affected} 行 / 价格入库 {steam_prices_affected}
行</td></tr>
  <tr><td>Epic</td><td>发现 {epic_count} 款 / 游戏入库 {epic_games_affected} 行 / 价格入库 {epic_prices_affected}
行</td></tr>
  <tr><td>合计</td><td>发现 {total_discovery} 款 / 入库 {total_affected} 行</td></tr>
</table>
    """.strip()

    summary = (

        f"Steam: 发现{steam_count}款 / 游戏入库{steam_games_affected}行 / 价格入库{steam_prices_affected}行\n"
        f"Epic: 发现{epic_count}款 / 游戏入库{epic_games_affected}行 / 价格入库{epic_prices_affected}行\n"
        f"合计: 发现{total_discovery}款 / 入库{total_affected}行"
    )

    return {
        "html": html,
        "summary": summary,
        "discovery_count": total_discovery,
        "affected_rows": total_affected,
    }