import re

def main(outputs: list) -> dict:
    games_values = []
    games_prefix = ""
    prices_values = []
    prices_prefix = ""

    for s in outputs:
        s = s.strip()
        if not s or "SKIP" in s:
            continue

        # 按每个 INSERT 语句拆分（用 ; 分割后再拼回）
        # 先按 ;\n 或 ; 拆成多个独立的 SQL 语句
        statements = re.split(r';\s*\n', s)

        for stmt in statements:
            stmt = stmt.strip()
            if not stmt or not stmt.upper().startswith("INSERT"):
                continue
            # 去掉可能的 ON DUPLICATE KEY UPDATE
            stmt = re.sub(r"\s+ON\s+DUPLICATE\s+KEY\s+UPDATE\s+.*$", "", stmt, flags=re.IGNORECASE |
                                                                                     re.DOTALL).strip()
            if not stmt.endswith(";"):
                stmt += ";"

            m = re.match(r"(INSERT\s+(?:IGNORE\s+)?INTO\s+(\w+)\s*\([^)]+\))\s*VALUES\s*(\(.+\))\s*;", stmt,
                         re.IGNORECASE | re.DOTALL)
            if m:
                table_name = m.group(2).lower()
                if table_name == "games":
                    games_prefix = m.group(1)
                    games_values.append(m.group(3))
                elif table_name == "game_prices":
                    prices_prefix = m.group(1)
                    prices_values.append(m.group(3))

    games_sql = ""
    prices_sql = ""
    games_count = 0
    prices_count = 0

    if games_values:
        prefix = re.sub(r"INSERT\s+IGNORE\s+INTO", "INSERT INTO", games_prefix, flags=re.IGNORECASE)
        games_sql = f"{prefix} VALUES {', '.join(games_values)} ON DUPLICATE KEY UPDATE release_date = VALUES(release_date), developer = VALUES(developer), publisher = VALUES(publisher), genres = VALUES(genres),summary = VALUES(summary);"
        games_count = len(games_values)

    if prices_values:
        # 把 appid=NULL 或 appid=0 替换为 0
        fixed_values = []
        for v in prices_values:
            v = re.sub(r'\(\s*NULL\s*,', '(0,', v, flags=re.IGNORECASE)
            fixed_values.append(v)
        prefix = re.sub(r"INSERT\s+IGNORE\s+INTO", "INSERT INTO", prices_prefix, flags=re.IGNORECASE)
        prices_sql = f"{prefix} VALUES {', '.join(fixed_values)} ON DUPLICATE KEY UPDATE initial_price = VALUES(initial_price), final_price = VALUES(final_price), discount_percent = VALUES(discount_percent);"
        prices_count = len(fixed_values)

    return {
        "games_count": games_count,
        "prices_count": prices_count,
        "games_sql": games_sql,
        "prices_sql": prices_sql,
    }