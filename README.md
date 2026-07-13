# 游戏数据自动化搜集与分析平台

基于 [Dify](https://dify.ai) 工作流的多源游戏信息自动化采集管线，每日自动从 Steam、Epic Games Store 和 Tavily 搜索引擎发现新游戏，提取详情与价格数据，存入 MySQL 数据库，并通过企业微信机器人推送日报。

## 架构概览

```
Steam RSS / API / HTML ──┐
Epic Games Store API ────┼──→ 迭代处理 ──→ LLM 生成 SQL ──→ MySQL ──→ HTML 报告 ──→ 企业微信推送
Tavily Search API ───────┘                                    (games + game_prices)
```

- **编排层**: Dify Workflow (YAML DSL)
- **执行层**: Dify 内置 Code Node (Python 3) + LLM Node + HTTP Request Node + SQL Execute Plugin
- **存储层**: MySQL (通过 Dify SQL Execute 插件)

## 数据源

| 来源 | 用途 | 端点 | 稳定性 |
|:---|:---|:---|:---|
| Steam RSS | 新游发现 | `store.steampowered.com/feeds/newreleases.xml` | 高 |
| Steam AppDetails API | 游戏详情+价格 | `store.steampowered.com/api/appdetails` | 中（CDN 反爬） |
| Epic Games Store API | 免费游戏发现 | `store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions` | 高 |
| Tavily Search API | 游戏信息补充 | `api.tavily.com/search` | 高 |
| Steam 搜索页 HTML | 新游后备发现 | `store.steampowered.com/search/` | 低（CDN 反爬） |
| Steam Featured API | 精选游戏后备 | `store.steampowered.com/api/featuredcategories` | 低（CDN 反爬） |

## 数据库表结构

### games

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT AUTO_INCREMENT | 主键 |
| name | VARCHAR(500) | 游戏名 |
| appid | INT | Steam AppID（Epic 游戏为 0） |
| release_date | VARCHAR(50) | 发售日期 |
| developer | VARCHAR(500) | 开发商 |
| publisher | VARCHAR(500) | 发行商 |
| genres | VARCHAR(500) | 游戏类型 |
| summary | TEXT | 游戏简介 |
| source | VARCHAR(50) | 数据来源 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### game_prices

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| id | INT AUTO_INCREMENT | 主键 |
| appid | INT NOT NULL DEFAULT 0 | Steam AppID |
| name | VARCHAR(500) | 游戏名 |
| currency | VARCHAR(10) | 货币代码（CNY/USD） |
| initial_price | DECIMAL(10,2) | 原价 |
| final_price | DECIMAL(10,2) | 现价 |
| discount_percent | INT | 折扣百分比 |
| recorded_at | DATE NOT NULL | 记录日期 |
| UNIQUE KEY | (appid, name, recorded_at) | 每日每游戏一条记录 |

## 工作流节点说明

| 节点 | 类型 | 说明 |
|:---|:---|:---|
| Steam 搜索 | Code | 4 源游戏发现（RSS → HTML → API → coming_soon），优雅降级 |
| Epic 搜索 | Code | Epic Games Store 免费游戏发现 |
| Game 请求 | Code | Steam AppDetails API 调用，提取详情+价格 |
| HTTP 请求 | HTTP | Tavily 搜索补充游戏信息 |
| 格式转换 | Code | SQL 查询结果 → appid/name 提取 |
| 生成SQL语句 | LLM | DeepSeek-chat 生成 INSERT 语句 |
| 执行SQL语句 | Code | games 与 game_prices 的 INSERT 拆分与合并 |
| SQL Execute | Plugin | 实际执行 SQL（需要 Dify SQL Execute 插件） |
| 报告生成 | Code | HTML 日报 + 摘要文本 |
| 消息推送 | Code | 企业微信机器人 Webhook 推送 |

## 部署步骤

### 1. 准备环境

- [Dify](https://github.com/langgenius/dify) 部署完成（Docker Compose 或云端版）
- MySQL 数据库（可与 Dify 共用 `db_postgres` 或独立部署）
- Dify 已安装 SQL Execute 插件
- 企业微信机器人 Webhook URL（可选）

### 2. 创建数据库表

```bash
mysql -u root -p < schema.sql
```

### 3. 导入工作流

在 Dify 控制台 → 工作室 → 导入 DSL 文件 → 选择 `workflow.yml`

### 4. 配置 API 密钥

工作流中需要配置：
- **Tavily API Key**: 搜索节点中的 `Authorization` 头
- **LLM 模型**: SQL 生成节点使用的模型 provider（默认 DeepSeek-chat）
- **MySQL 连接**: SQL Execute 插件的数据库连接信息
- **企业微信 Webhook**: 推送节点的 Webhook URL

### 5. 配置沙箱超时

编辑 `dify/docker/.env`：

```env
CODE_EXECUTION_READ_TIMEOUT=300
SANDBOX_WORKER_TIMEOUT=300
```

重启 Dify 服务使配置生效。

### 6. 设置定时运行

在 Dify 工作流设置中配置定时触发器，建议每日 10:00 运行一次。

## Code Snippets 目录

`code_snippets/` 中包含工作流所有 Code 节点的独立 Python 文件，便于：

- 版本管理与 diff 追踪
- 本地调试与单元测试
- 直接在 Dify Code 节点中粘贴使用

| 文件 | 对应节点 |
|:---|:---|
| `Steam_search.py` | Steam 搜索 — 多源游戏发现 |
| `Epic_search.py` | Epic 搜索 — Epic 免费游戏发现 |
| `Game_request.py` | Game 请求 — Steam AppDetails 详情+价格提取 |
| `Execute_SQL.py` | 执行SQL语句 — SQL 拆分合并 |
| `Report_generation.py` | 报告生成 — HTML 日报 |
| `Format_conversion.py` | 格式转换 — SQL 结果解析 |
| `Quote_fix.py` | SQL 转义处理 |

## 设计决策

### 为什么不用 Scrapy/爬虫框架？

整个项目在 Dify 沙箱（`langgenius/dify-sandbox`）中运行，仅能使用 Python 标准库（`urllib`、`ssl`、`xml`）。不能 `pip install` 第三方包。所有网络请求通过 Dify 的 SSRF 代理（Squid）转发。

### 为什么用 Steam RSS 而不是 API？

Steam CDN（Akamai）会检测并封禁服务器 IP 的 API 请求。RSS feed（`newreleases.xml`）是 Steam 官方提供的 XML 订阅源，反爬策略宽松，返回 30 款游戏且包含 AppID。详见 [Steam CDN 反爬分析](docs/steam-cdn-analysis.md)。

### 价格追踪设计

- Steam：直接调用 `appdetails` API，从 `price_overview` 字段提取（单位：分 → 元）
- Epic：免费游戏，价格记为 0
- 去重：`(appid, name, recorded_at)` 组合唯一键，每日同款游戏只保留最新价格

## 致谢

- [Dify](https://dify.ai) — AI 工作流编排平台
- [Steam](https://store.steampowered.com) — 游戏数据源
- [Epic Games](https://www.epicgames.com) — 免费游戏数据
- [Tavily](https://tavily.com) — AI 搜索 API
