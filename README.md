# windflex-system

自动化测试系统核心代码和配置仓库

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
