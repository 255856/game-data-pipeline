def main(item: str) -> dict:
    escaped = item.replace("'", "''")
    return {"game_name": escaped}