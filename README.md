# 19-curtainlen（窗帘用布）

Curtainlen — 成品宽×褶倍率 + 上下边折；换算布长米数

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4800 |
| API | http://localhost:9800 |

## 主链

窗宽层高+褶量 → 布长 → 窗户示意

整匹起订托底：布料可声明起订米数 M，订货米数 = max(基础米数, M)；M 非正校验失败不写历史；保存固化基础米/M/订货米快照，改布料默认 M 不回写旧单。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
