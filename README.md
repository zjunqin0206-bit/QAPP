# QAPP-基于深度学习的毕业论文系统设计

本项目是一个“Vue 前端 + Java 后端 + Python 深度学习”的整合项目模版，模版使用一个简单的两层的全连接神经网络，用于鸢尾花数据集的三分类，项目体现的工作量如下：
- 登录/注册/修改密码
- Iris 数据管理（查询、筛选、增删改）
- 模型训练、训练结果展示、预测

本文档共分为三部分第一部分，介绍各模块的内容。第二部分，给出将此项目可以运行在本地的方案。第三部分，给出使用 Decbox 和 Cursor 实现从零开始快速完成一个毕业设计的方案。

## 1. 项目目录与模块作用

### 1.1 `back/`（Java 后端）
- 技术栈：Spring Boot + MyBatis + MySQL
- 负责：
  - 账号接口：注册、登录、修改密码、退出
  - Iris 接口：列表、筛选、按 ID 查询、新增、修改、删除
  - 启动初始化：账号表、默认账号、Iris 表、空表种子数据
- 默认端口：`3000`

### 1.2 `front/`（Vue 前端）
- 技术栈：Vue3 + Vite + Axios + Vue Router
- 负责：
  - 用户登录与页面路由
  - 数据管理、训练任务提交、结果展示、预测页面
- 默认端口：`5173`

### 1.3 `dl/service/`（Python 训练服务）
- 技术栈：FastAPI + PyTorch + scikit-learn
- 负责：
  - 从 MySQL 读取 Iris 数据
  - 创建/轮询训练任务
  - 输出指标、混淆矩阵、图像
  - 执行单样本预测
- 默认端口：`3001`

### 1.4 `dl/prototype/`
- 本地实验代码（原型验证），不影响主业务部署。

---

## 2. 你的数据库当前结构（已连接实查）

我已连接你提供的数据库并读取真实结构：
- 库：`iris_db`
- 表：`iris`（150 条）
- 表：`tb_account`（3 条）

### 2.1 `iris` 表

```sql
CREATE TABLE `iris` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sepal_length` decimal(3,1) DEFAULT NULL,
  `sepal_width` decimal(3,1) DEFAULT NULL,
  `petal_length` decimal(3,1) DEFAULT NULL,
  `petal_width` decimal(3,1) DEFAULT NULL,
  `class` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2.2 `tb_account` 表

```sql
CREATE TABLE `tb_account` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_salt` varchar(128) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 3. 本地部署前准备

## 3.1 软件版本
- Git
- JDK `17`
- Maven `3.6+`
- Node.js `18+`（建议 LTS）
- Python `3.10+`
- MySQL `8.x`

## 3.2 克隆项目

```bash
git clone https://github.com/zjunqin0206-bit/QAPP.git
cd QAPP
```

---

## 4. 连接信息在什么文件里

这是你特别关心的点，按模块列出：

### 4.1 Java 后端数据库连接（back）
文件：`back/src/main/resources/application.yml`

已改为环境变量写法：
- `DB_URL`
- `DB_USER`
- `DB_PASSWORD`

如果不传，会使用本地默认：
- `jdbc:mysql://127.0.0.1:3306/iris_db...`
- `root / 123456`

### 4.2 Python 训练服务数据库连接（dl/service）
文件：`dl/service/app.py`

读取环境变量：
- `DB_URL`

默认值：
- `mysql://root:123456@127.0.0.1:3306/iris_db`

### 4.3 前端接口目标地址（front）
文件：`front/.env.local`（由 `.env.example` 复制）
- `VITE_IRIS_API_PROXY_TARGET`（Java 后端地址）
- `VITE_TRAIN_API_PROXY_TARGET`（训练服务地址）

---

## 5. 如何构建数据库（两种方式）

## 方式 A：自动初始化（推荐新手）
1. 先创建空库 `iris_db`。
2. 启动后端 `back`。
3. 后端会自动创建 `tb_account`、`iris`，并在 `iris` 空表时灌入种子数据。

只需执行：

```sql
CREATE DATABASE IF NOT EXISTS iris_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
```

## 方式 B：手工建表（你想完全可控时）

```sql
USE iris_db;

CREATE TABLE IF NOT EXISTS tb_account (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password_salt VARCHAR(128) NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS iris (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  sepal_length DOUBLE NOT NULL,
  sepal_width DOUBLE NOT NULL,
  petal_length DOUBLE NOT NULL,
  petal_width DOUBLE NOT NULL,
  `class` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 6. 本地启动步骤（严格顺序）

## 6.1 启动 MySQL
确认本机 MySQL 已启动，并存在 `iris_db`。

## 6.2 启动 Java 后端

```bash
cd back

# Linux/macOS
export DB_URL='jdbc:mysql://127.0.0.1:3306/iris_db?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true'
export DB_USER='root'
export DB_PASSWORD='你的数据库密码'

mvn spring-boot:run
```

启动成功后访问：
- `http://localhost:3000/api/iris/list`

## 6.3 启动 Python 训练服务

```bash
cd dl/service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DB_URL='mysql://root:你的数据库密码@127.0.0.1:3306/iris_db'
uvicorn app:app --host 0.0.0.0 --port 3001
```

启动成功后访问：
- `http://localhost:3001/docs`

## 6.4 启动前端

```bash
cd front
npm install
cp .env.example .env.local
```

编辑 `front/.env.local`：

```env
VITE_IRIS_API_PROXY_TARGET=http://localhost:3000
VITE_TRAIN_API_PROXY_TARGET=http://localhost:3001
```

启动：

```bash
npm run dev
```

打开：
- `http://localhost:5173`

---

## 7. 常见报错与解决

## 7.1 `No plugin found for prefix 'springboot'`
原因：命令写错。
正确命令：
```bash
mvn spring-boot:run
```

## 7.2 后端启动报数据库连接失败
- 检查 `DB_URL / DB_USER / DB_PASSWORD`
- 检查 MySQL 是否可访问
- 检查库名是否 `iris_db`

## 7.3 前端能打开但接口报 404/代理失败
- 检查 `front/.env.local` 的两个 target
- 检查 `3000` 和 `3001` 服务是否已启动

## 7.4 训练服务启动失败（缺依赖）
- 确认已激活 `.venv`
- 重新执行 `pip install -r requirements.txt`

---

## 8. 安全规范（必须看）

不要把以下信息提交到 GitHub：
- 数据库用户名/密码
- 内网数据库地址
- 完整连接串
- Token、私钥、密钥

建议：
- 使用 `.env` / `.env.local` 存储敏感配置
- 使用 Secret 管理服务保存生产凭据
- 一旦泄露，立即轮换密码和令牌

