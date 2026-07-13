def main(sql_output: list) -> dict:
    """
    从 SQL 查询结果中提取 appid 和 name
    输入格式: [{"result": [{"appid": 730}]}]
    """
    try:
        # sql_output 是一个数组，取第一个元素
        if not sql_output or len(sql_output) == 0:
            return {
                "appid": None,
                "name": None,
                "has_data": False
            }

        # 取第一个元素
        first_item = sql_output[0]

        # 获取 result 数组
        result = first_item.get("result", [])

        # 判断是否有数据
        has_data = len(result) > 0

        # 提取数据
        appid = None
        name = None

        if has_data:
            game_data = result[0]
            appid = game_data.get("appid")
            name = game_data.get("name")

        return {
            "appid": appid,
            "name": name,
            "has_data": has_data
        }

    except Exception as e:
        return {
            "appid": None,
            "name": None,
            "has_data": False,
            "error": str(e)
        }