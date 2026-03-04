# windflex-system

Windflex 自动化测试系统 - 系统代码与配置仓库（第一期原型）

## 快速启动

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env   # 必填：BOARD_IP

# 2. 启动全部服务
docker compose up -d

# 3. API 文档: http://localhost:8000/docs
# 4. Jenkins:  http://localhost:8080  (admin / windflex_admin)
```

## 服务

| 服务 | 端口 | 说明 |
|------|------|------|
| hardware-service | 8000 | 板子 SSH/ADB/串口控制 REST API |
| jenkins | 8080 | CI/CD + Robot Framework |
| postgres | 5432 | 测试结果数据库 |
| redis | 6379 | 缓存 |

## 本地开发

```bash
cd services/hardware-service
pip install -r requirements.txt
BOARD_IP=192.168.1.100 POWER_MODEL=Non-programmable python main.py
# 单元测试
pytest tests/ -v
```

## 组件
- **Jenkins Server**: CI/CD 和测试管理
- **OpenCLaw**: AI Gateway，支持 LLM 生成测试用例和失败分析
- **Hardware Service**: 电源、ADB、串口、SSH 控制服务

## 快速开始

```bash
# 配置环境变量
cp .env.example .env
vim .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

更多信息请参考完整文档。
