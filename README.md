# 电商数据分析 Agent

提交分析任务，得到带数字来源的分析报告。当前是第 1 周：数据库、只读账号和 Olist 数据。

## 环境

Python 3.14，Docker Desktop。数据库地址使用 `127.0.0.1`，不要用 `localhost`。在这台机器上 `localhost` 会先尝试 IPv6，连接要空等几秒。

## 启动

```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
docker compose up -d