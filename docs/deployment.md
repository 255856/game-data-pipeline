# 部署指南

## 前提条件

- 已部署 Dify（Docker Compose 或云服务）
- MySQL 5.7+ 或 8.0+（可与 Dify PostgreSQL 共存）
- 企业微信机器人 Webhook URL（可选，用于日报推送）

## 步骤 1：创建数据库

```bash
mysql -u root -p < schema.sql
```

## 步骤 2：安装 SQL Execute 插件

Dify 控制台 → 插件 → 搜索 `SQL Execute` → 安装

## 步骤 3：配置沙箱超时

编辑 Dify 项目目录下的 `docker/.env`：

```env
CODE_EXECUTION_READ_TIMEOUT=300
SANDBOX_WORKER_TIMEOUT=300
```

重启 Dify：

```bash
cd dify/docker
docker compose restart api worker worker_beat sandbox
```

## 步骤 4：导入工作流

1. Dify 控制台 → 工作室 → 导入 DSL 文件
2. 选择 `workflow.yml`
3. 导入后会看到完整的工作流图谱

## 步骤 5：配置节点

### 5.1 LLM 节点（生成SQL语句）

- 选择模型 provider（推荐 DeepSeek-chat）
- 确保 API Key 已配置

### 5.2 Tavily HTTP 请求节点

节点 `Steam_HTTP 请求` 的 Authorization 头需要填入 Tavily API Key：

```
Authorization: tvly-dev-YOUR_KEY_HERE
```

在 [tavily.com](https://tavily.com) 注册获取。

### 5.3 SQL Execute 节点

两个 SQL Execute 节点需要配置相同的数据库连接：

| 参数 | 值 |
|:---|:---|
| Host | 你的 MySQL 主机地址 |
| Port | 3306 |
| Database | dify_test |
| Username | root |
| Password | 你的密码 |

### 5.4 企业微信推送节点

节点 `消息推送` 中配置 Webhook URL：

```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

## 步骤 6：配置定时运行

Dify 控制台 → 工作流设置 → 定时触发器：

- **Cron**: `0 2 * * *`（每日北京时间 10:00）
- **时区**: Asia/Shanghai
- **失败重试**: 开启

## 步骤 7：测试运行

1. 点击 "运行" 按钮手动触发一次
2. 检查日志输出，确认各节点执行正常
3. 验证数据库中游戏和价格数据已写入
4. 确认企业微信收到推送消息

## 常见问题

### Q: 代码执行超时

错误: `Code execution timed out`

增大 `.env` 中的超时值，然后重启 Dify：

```env
CODE_EXECUTION_READ_TIMEOUT=600
```

### Q: Steam 搜索全部失败

错误: `rss: URLError; popular: URLError; featured: URLError; coming: URLError`

Steam CDN 封了服务器 IP。等待几小时到一天通常会自动解封。在此期间管线仍可通过 Epic + Tavily 产出部分结果。

### Q: SQL 执行报错 "table doesn't exist"

确认已执行 `schema.sql`，且 SQL Execute 插件连接的数据库与建表数据库一致。

### Q: 企业微信推送无反应

1. 检查 Webhook URL 是否正确
2. 在浏览器中直接 POST 测试 Webhook 是否可用
3. 检查推送节点代码中的 `webhook_url` 变量

### Q: Nginx 502 Bad Gateway

Docker 容器重启后 IP 变化导致 nginx 缓存失效：

```bash
docker restart docker-nginx-1
```
