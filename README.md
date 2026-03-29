# QAPP 项目说明

QAPP 是一个前后端与深度学习服务协同的整合项目，围绕 Iris（鸢尾花）数据提供账号认证、数据管理、模型训练与预测能力。

## 一、模块内容与作用

### 1. `back/`（Java 后端）
- 技术栈：Spring Boot + MyBatis + MySQL
- 主要职责：
  - 提供账号注册、登录、修改密码等认证接口
  - 提供 Iris 数据查询、筛选、增删改接口
  - 启动时自动执行基础初始化：账号表、默认账号、Iris 表与空表种子数据
- 默认端口：`3000`

### 2. `front/`（Vue 前端）
- 技术栈：Vue 3 + Vite + Axios + Vue Router
- 主要职责：
  - 提供登录与业务页面
  - 调用后端数据接口与训练服务接口
  - 展示训练进度、训练结果与预测结果
- 默认端口：`5173`

### 3. `dl/`（Python 深度学习模块）

#### `dl/prototype/`
- 本地实验代码，用于数据处理、训练流程探索与验证。

#### `dl/service/`
- 技术栈：FastAPI + PyTorch + scikit-learn
- 主要职责：
  - 从 MySQL 加载训练数据
  - 创建训练任务并支持轮询进度
  - 输出混淆矩阵、分类指标与图像产物
  - 提供单样本预测接口
- 默认端口：`3001`

## 二、如何在本地运行

## 1) 环境准备
- JDK `17`
- Maven `3.6+`
- Node.js `18+`（建议 LTS）
- Python `3.10+`
- MySQL `8.x`

## 2) 克隆项目
```bash
git clone https://github.com/zjunqin0206-bit/QAPP.git
cd QAPP
```

## 3) 启动 Java 后端（`back/`）
```bash
cd back
mvn spring-boot:run
```

启动后可访问：
- 后端地址：`http://localhost:3000`
- 示例接口：`http://localhost:3000/api/iris/list`

说明：
- 当前后端会在连接数据库成功后，自动检查并初始化 `tb_account`、`iris` 及空表种子数据。

## 4) 启动训练服务（`dl/service/`）
```bash
cd dl/service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 按你的本地数据库实际信息设置
export DB_URL="mysql://<user>:<password>@<host>:3306/iris_db"

uvicorn app:app --host 0.0.0.0 --port 3001
```

启动后可访问：
- 训练服务地址：`http://localhost:3001`
- Swagger 文档：`http://localhost:3001/docs`

## 5) 启动前端（`front/`）
```bash
cd front
npm install
cp .env.example .env.local
```

建议在 `.env.local` 中配置：
```bash
VITE_IRIS_API_PROXY_TARGET=http://localhost:3000
VITE_TRAIN_API_PROXY_TARGET=http://localhost:3001
```

然后启动：
```bash
npm run dev
```

访问：`http://localhost:5173`

## 6) 联调顺序建议
1. 先启动 MySQL
2. 再启动 `back`
3. 再启动 `dl/service`
4. 最后启动 `front`

## 三、数据库信息是否要上传到 GitHub？

不要上传。

下面这些内容都不应提交到公开仓库：
- 数据库用户名/密码
- 内网数据库地址
- 完整连接串（例如 `mysql://root:password@host:3306/...`）
- 各类 Token、密钥、私钥

建议做法：
- 使用 `.env` / `.env.local`（并加入 `.gitignore`）管理敏感配置
- 生产环境使用平台 Secret 管理能力（CI/CD Secret、容器 Secret 等）
- 如果敏感信息已经提交过仓库，立即轮换密码与令牌

