import json


def main(games_data: list, prices_data: list) -> dict:
    """
    将 SQL 查询结果转换为 HTML 表格
    支持 Dify SQL Execute 节点的多种输出格式
    """

    def extract_rows(data):
        """递归提取数据行，兼容多种 Dify 输出格式"""
        rows = []

        if not data:
            return rows

        # 如果是列表，遍历每个元素
        if isinstance(data, list):
            for item in data:
                rows.extend(extract_rows(item))
            return rows

        # 如果是字典
        if isinstance(data, dict):
            # 1. 如果有 result 字段（SQL Execute 标准输出）
            if "result" in data:
                result = data["result"]
                if isinstance(result, list):
                    rows.extend(result)
                elif isinstance(result, dict):
                    rows.append(result)
            # 2. 如果有 data 字段（某些版本）
            elif "data" in data:
                data_field = data["data"]
                if isinstance(data_field, list):
                    rows.extend(data_field)
                elif isinstance(data_field, dict):
                    rows.append(data_field)
            # 3. 如果有 text 字段（SQL 执行结果描述），忽略
            elif "text" in data:
                # text 是执行结果描述，不是数据，跳过
                pass
            # 4. 如果字典本身看起来像一条数据记录（有 name 字段等）
            elif "name" in data or "appid" in data:
                rows.append(data)
            # 5. 如果字典包含其他可能的数据字段，尝试直接提取
            else:
                # 尝试提取所有值中可能是列表的部分
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        rows.extend(extract_rows(value))

        return rows

    # 提取游戏数据
    games = extract_rows(games_data) if games_data else []
    prices = extract_rows(prices_data) if prices_data else []

    # 去重（防止重复数据）
    unique_games = []
    seen = set()
    for g in games:
        key = (g.get("name", ""), g.get("release_date", ""))
        if key not in seen:
            seen.add(key)
            unique_games.append(g)
    games = unique_games

    # === 生成游戏列表 HTML ===
    game_cols = ["name", "release_date", "developer", "publisher", "genres", "summary"]
    game_cn = ["游戏名", "发售日期", "开发商", "发行商", "类型", "简介"]

    html = "<h3>游戏列表</h3>"
    if games:
        html += f"<p>共 {len(games)} 款游戏</p>"
        html += "<table border='1' style='border-collapse:collapse;width:100%;font-size:14px;'>"
        html += "<tr style='background-color:#f0f0f0;'>"
        html += "<th>序号</th>" + "".join(
            f"<th style='padding:8px;text-align:left;'>{c}</th>" for c in game_cn) + "</tr>"

        for idx, row in enumerate(games, 1):
            bgcolor = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color:{bgcolor};'>"
            html += f"<td style='padding:6px;'>{idx}</td>"
            for c in game_cols:
                val = row.get(c, '')
                if val is None:
                    val = ''
                # 截断过长的简介
                if c == "summary" and len(str(val)) > 100:
                    val = str(val)[:100] + "..."
                html += f"<td style='padding:6px;'>{val}</td>"
            html += "</tr>"
        html += "</table>"
    else:
        html += "<p>暂无游戏数据</p>"

    # === 生成价格列表 HTML ===
    price_cols = ["name", "currency", "initial_price", "final_price", "discount_percent", "recorded_at"]
    price_cn = ["游戏名", "货币", "原价", "现价", "折扣", "记录时间"]

    html += "<h3>价格记录</h3>"
    if prices:
        html += f"<p>共 {len(prices)} 条价格记录</p>"
        html += "<table border='1' style='border-collapse:collapse;width:100%;font-size:14px;'>"
        html += "<tr style='background-color:#f0f0f0;'>"
        html += "<th>序号</th>" + "".join(
            f"<th style='padding:8px;text-align:left;'>{c}</th>" for c in price_cn) + "</tr>"

        for idx, row in enumerate(prices, 1):
            bgcolor = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color:{bgcolor};'>"
            html += f"<td style='padding:6px;'>{idx}</td>"
            for c in price_cols:
                val = row.get(c, '')
                if val is None:
                    val = ''
                if c == "discount_percent" and val:
                    # 折扣显示为百分比
                    html += f"<td style='padding:6px;color:green;font-weight:bold;'>{val}%</td>"
                elif c == "currency":
                    html += f"<td style='padding:6px;'>{val}</td>"
                else:
                    html += f"<td style='padding:6px;'>{val}</td>"
            html += "</tr>"
        html += "</table>"
    else:
        html += "<p>暂无价格数据</p>"

    return {"html": html}