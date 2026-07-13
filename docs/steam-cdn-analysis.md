# Steam CDN 反爬分析与应对

## 问题描述

从服务器 IP 直接请求 Steam API（`store.steampowered.com/api/*`）时，Akamai CDN 会检测非浏览器流量并封禁 IP。

## 现象时序

| 阶段 | 表现 | 原因 |
|:---|:---|:---|
| 首次部署 | 所有 API 正常 | IP 未被标记 |
| 运行 1-2 天 | 部分 API 超时 | CDN 开始限速 |
| 持续运行 | 全部 API URLError | IP 被完全封禁 |
| 等待数小时 | RSS 恢复，API 仍封 | CDN 部分解封 |

## 技术分析

### 被封原因

1. **缺失关键 HTTP 头** — 初始代码仅有 `User-Agent`，没有 `Accept`、`Accept-Language`、`Accept-Encoding`
2. **请求频率** — 迭代器并行 10 个请求，短时间内大量 API 调用触发风控
3. **服务器 IP 特征** — 云服务器 IP 段被 Steam CDN 标记为高风险

### 哪些端点受影响

| 端点 | 用途 | 封锁程度 |
|:---|:---|:---|
| `api/featuredcategories` | 精选分类 | 严重 |
| `search/?filter=popularnew` | 热门新品 HTML | 严重（间歇） |
| `search/?filter=comingsoon` | 即将推出 HTML | 严重 |
| `api/appdetails?appids=X` | 游戏详情 | 中等（间歇） |
| `feeds/newreleases.xml` | RSS 新品 | 较轻 |
| `feeds/popular.xml` | RSS 热门 | 中等（间歇） |

## 解决方案

### 当前方案：RSS 为主 + 多源降级

```
RSS (70% 成功率) → HTML 搜索 → Featured API → 即将推出
```

RSS feed 是 Steam 官方提供的 XML 订阅源（给 RSS 阅读器用的），反爬策略最宽松。它返回 30 款游戏且包含 AppID，信息量足够。

### 已实施的缓解措施

1. 所有请求添加完整的浏览器 Headers（`Accept`、`Accept-Language`、`Accept-Encoding`）
2. 不稳定源超时降至 15s，减少等待时间
3. 每个源独立 try/except，互不影响
4. RSS 源 2 次重试机制

### 可选的长远方案

| 方案 | 优点 | 缺点 |
|:---|:---|:---|
| Steam Web API Key | 官方支持，不限流 | 需要出版方账户 |
| 代理轮换 | 绕过 IP 封禁 | 成本高，维护复杂 |
| 换用国内数据源 | 彻底解决 | 数据可能不全 |
| 降低请求频率 | 延缓封禁 | 不能根治 |

## 测试方法

进入 Dify 沙箱测试连通性：

```bash
docker exec docker-sandbox-1 python3 -c "
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://store.steampowered.com/feeds/newreleases.xml?cc=cn')
req.add_header('Accept', 'application/xml')
resp = urllib.request.urlopen(req, timeout=15, context=ctx)
print('RSS OK' if resp.status == 200 else f'Status {resp.status}')
"
```
