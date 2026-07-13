import json

def main(raw: str) -> dict:
    try:
        obj = json.loads(raw) if isinstance(raw, str) else raw
    except:
        return {"info": raw if raw else ""}

    parts = []
    results = obj.get("results", [])
    for r in results[:3]:
        title = r.get("title", "")
        content = r.get("content", "")
        if content:
            parts.append(f"标题: {title}\n内容: {content[:500]}")

    return {"info": "\n\n".join(parts) if parts else ""}