# QAPP-基于深度学习的毕业论文系统设计

本项目是一个“Vue 前端 + Java 后端 + Python 深度学习”的整合项目模版，适合用于涉及到机器学习或深度学习的应用型毕业论文系统设计。模版使用一个简单的两层的全连接神经网络，用于鸢尾花数据集的三分类，项目体现的工作量如下：

- 登录/注册/修改密码
- Iris 数据管理（查询、筛选、增删改）
- 模型训练、训练结果展示、预测

本文档共分为三部分。第一部分介绍各模块的内容，第二部分给出将此项目运行在本地的方案，第三部分给出使用 Sealos 和 Cursor 从零开始快速完成一个毕业设计的方案。

## 1. 模块作用与效果展示

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

### 1.5 效果展示

![截屏2026-03-30 17.10.26](/Users/mac/Downloads/img/截屏2026-03-30 17.10.26.png)

![截屏2026-03-30 17.11.58](/Users/mac/Downloads/img/截屏2026-03-30 17.11.58.png)

![截屏2026-03-30 17.12.10](/Users/mac/Downloads/img/截屏2026-03-30 17.12.10.png)

![截屏2026-03-30 17.12.40](/Users/mac/Downloads/img/截屏2026-03-30 17.12.40.png)

![截屏2026-03-30 17.13.18](/Users/mac/Downloads/img/截屏2026-03-30 17.13.18.png)

![截屏2026-03-30 17.13.48](/Users/mac/Downloads/img/截屏2026-03-30 17.13.48.png)

---

## 2. 本地部署

### 2.1 本地数据库的建立

本项目运行依赖一个 MySQL 数据库，库名建议统一使用 `iris_db`。如果你是第一次部署，建议先完成数据库，再启动后端和训练服务。

本项目实际使用两张核心表：

- `iris`：保存鸢尾花样本数据，用于数据管理和模型训练
- `tb_account`：保存系统账号信息，用于登录、注册和密码修改

#### 2.1.1 准备环境

本地需要提前安装：

- MySQL `8.x`
- Navicat、DataGrip、DBeaver 或 MySQL 命令行客户端，任选其一

#### 2.1.2 创建数据库

登录你的 MySQL 后，执行：

```sql
CREATE DATABASE IF NOT EXISTS iris_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
```

然后切换到该数据库：

```sql
USE iris_db;
```

#### 2.1.3 创建数据表

执行下面两段 SQL：

```sql
CREATE TABLE IF NOT EXISTS tb_account (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password_salt VARCHAR(128) NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```sql
CREATE TABLE IF NOT EXISTS iris (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  sepal_length DOUBLE NOT NULL,
  sepal_width DOUBLE NOT NULL,
  petal_length DOUBLE NOT NULL,
  petal_width DOUBLE NOT NULL,
  `class` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### 2.1.4 导入数据

- 下载数据集：https://archive.ics.uci.edu/dataset/53/iris
- 将数据集导入数据库中。

#### 2.1.5 建库完成后的检查方法

执行以下 SQL 确认数据库已经准备好：

```sql
SHOW TABLES;
SELECT COUNT(*) FROM iris;
SELECT COUNT(*) FROM tb_account;
```

如果 `SHOW TABLES` 能看到 `iris` 和 `tb_account`，说明数据库结构已经建立完成。

---

### 2.2 `back/` 配置修改

当别人将本项目部署到自己的电脑上时，`back/` 模块最需要关注的是数据库连接配置。因为源码中的 `application.yml` 已经写死了一个固定的 MySQL 地址、用户名和密码，这些配置通常并不适用于其他人的本地环境。

后端配置文件位置：

- `back/src/main/resources/application.yml`

部署者通常需要检查并修改以下内容：

- `spring.datasource.url`
- `spring.datasource.username`
- `spring.datasource.password`
- `server.port`（如果本机 `3000` 端口被占用）

推荐将数据库连接修改为自己的本地 MySQL，例如：

```yml
server:
  port: 3000

spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://127.0.0.1:3306/iris_db?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true
    username: root
    password: 你的数据库密码
```

完成配置修改后，进入 `back/` 目录启动项目：

```bash
cd back
mvn spring-boot:run
```

启动成功后，可通过下面的地址检查后端是否已经连通数据库：

```text
http://localhost:3000/api/iris/list
```

如果浏览器能返回 JSON 数据，说明后端已经启动成功，并且已经能够访问本地数据库。

需要说明的是，后端启动后会自动执行初始化逻辑：

- 如果 `tb_account` 表不存在，会自动建表
- 如果 `iris` 表不存在，会自动建表
- 如果 `tb_account` 中没有 `admin` 账号，会自动创建默认账号
- 如果 `iris` 表为空，会自动插入少量示例数据

因此，部署者通常不需要修改后端业务代码，只需要把数据库配置改成自己本地可用的配置即可。

### 2.3 `dl/` 配置修改

`dl/service/` 是本项目的 Python 深度学习训练服务。它负责从 MySQL 读取 Iris 数据，创建训练任务，计算结果指标，并提供预测接口。

该模块最关键的配置同样是数据库连接。源码中的 `app.py` 给 `DB_URL` 提供了默认值，而这个默认值同样指向一个固定服务器，因此别人本地部署时必须改成自己的数据库地址。

训练服务主文件位置：

- `dl/service/app.py`

部署者需要重点确认：

- `DB_URL` 是否指向自己的本地数据库
- 本机是否安装了 Python 依赖
- 本机是否能够正常运行 `uvicorn`

推荐的启动方式是通过环境变量覆盖数据库连接，而不是直接依赖源码中的默认值：

```bash
cd dl/service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DB_URL='mysql://root:你的数据库密码@127.0.0.1:3306/iris_db'
uvicorn app:app --host 0.0.0.0 --port 3001
```

如果部署者不想使用环境变量，也可以直接修改 `app.py` 中默认的 `DB_URL`，但这种方式不如环境变量灵活。

启动成功后，可访问：

```text
http://localhost:3001/docs
```

如果能够打开 Swagger 文档页面，说明训练服务已经正常启动。

这里还需要额外提醒两点：

- 训练服务依赖 `torch`、`fastapi`、`pymysql`、`scikit-learn` 等 Python 包，因此第一次部署时必须先执行 `pip install -r requirements.txt`
- 训练服务不会把训练模型长期保存到数据库中，训练任务和模型对象主要保存在当前 Python 进程内存中，因此服务重启后，之前训练出的模型不能直接继续使用

### 2.4 `front/` 配置修改

`front/` 是本项目的 Vue 前端。部署到别人本地时，前端本身一般不需要改业务代码，但必须检查前端访问后端和训练服务的地址是否正确。

从源码实现来看，前端分两类接口：

- 普通业务接口，通过 `src/api/http.js` 访问 Java 后端
- 训练与预测接口，通过 `src/api/train.js` 访问 Python 训练服务

因此，本地部署时需要重点修改的是前端环境变量配置文件。

建议部署者先进入前端目录并安装依赖：

```bash
cd front
npm install
```

然后在前端目录中创建本地环境变量文件，例如：

```bash
cp .env.example .env.local
```

接着把前端访问地址改成自己本地实际运行的服务地址，例如：

```env
VITE_API_BASE_URL=http://localhost:3000
VITE_TRAIN_API_BASE_URL=http://localhost:3001
```

如果部署者使用的是代理方案，也可以根据自己的 `vite.config.js` 规则改成对应代理变量。核心原则只有一条：前端必须能够正确访问到本地启动的 Java 后端和 Python 训练服务。

完成配置后，在 `front/` 目录启动前端：

```bash
npm run dev
```

启动成功后，浏览器访问：

```text
http://localhost:5173
```

如果页面可以正常打开，并且登录、数据管理、训练、预测都能正常请求接口，就说明前端配置已经正确。

### 2.5 项目运行完成

当数据库、后端、训练服务和前端都配置完成后，整个项目的本地运行顺序建议如下：

1. 先确认 MySQL 已启动，并且 `iris_db` 数据库已经建立完成
2. 启动 `back/`
3. 启动 `dl/service/`
4. 启动 `front/`

项目运行完成后，可以按下面顺序检查：

1. 打开 `http://localhost:3000/api/iris/list`
    如果能返回数据，说明后端正常。

2. 打开 `http://localhost:3001/docs`
    如果能看到接口文档，说明训练服务正常。

3. 打开 `http://localhost:5173`
    如果能进入前端页面，说明前端正常。

4. 使用默认账号或自行注册账号登录系统
    如果可以成功登录，说明认证模块正常。

5. 进入“数据管理”页面查看列表
    如果能显示 Iris 数据，说明前后端与数据库通信正常。

6. 进入“模型训练”页面提交一次训练任务
    如果能看到训练进度并最终跳转到结果页，说明前端、训练服务和数据库之间的联动正常。

7. 进入“预测”页面执行一次预测
    如果能够得到分类结果，说明项目整体运行完成。

到这里，说明该项目已经成功部署到本地，可以继续用于演示、论文撰写或后续功能扩展。

---

## 3. 使用 Sealos 和 Cursor 快速完成毕业设计

本章介绍如何借助 Sealos 和 Cursor 更标准化地完成一个前后端项目的搭建与开发。对于毕业设计项目而言，Sealos 更适合提供统一的开发环境、数据库和运行空间，Cursor 更适合承担代码生成、页面开发、问题调整和持续迭代等工作。将两者结合使用，可以明显提高项目从“搭好环境”到“完成开发”的整体效率。

本章内容主要参考以下资料：

- Sealos：[https://hzh.sealos.run/](https://hzh.sealos.run/)
- Cursor：[https://cursor.com/start-download](https://cursor.com/start-download)
- 参考视频：[https://www.bilibili.com/video/BV124D5YEEAD/](https://www.bilibili.com/video/BV124D5YEEAD/)

### 3.1 项目建立

首先需要在 Sealos 上完成数据库和项目运行环境的建立。对于一个完整的毕业设计项目，通常至少需要准备数据库、后端服务、前端项目以及其他辅助模块。在数据库中创建所需的库表，在 DevBox 中建立各个模块的工作目录和运行环境。完成这些操作后，可以在详情页中查看数据库连接信息、服务端口以及访问地址等内容。

当云端项目环境准备完成之后，就可以使用 Cursor 打开对应的项目目录，开始进行代码开发。这样做的优点是，开发环境、数据库和运行环境都相对统一，可以减少本地环境差异带来的问题，也更方便后续演示和部署。

![截屏2026-03-30 17.44.30](/Users/mac/Downloads/img/截屏2026-03-30 17.44.30.png)

![截屏2026-03-30 17.44.21](/Users/mac/Downloads/img/截屏2026-03-30 17.44.21.png)

### 3.2 构建流程

在使用 Sealos 和 Cursor 进行项目开发时，可以采用如下流程：

1. 完成后端的代码。
2. 保存测试用例。
3. 完成前端代码。
4. 利用测试用例完成前后端的对接。

这个流程的核心思想是先完成接口，再完成页面，最后进行联调。这样做的好处在于，后端接口、数据结构和测试结果会先稳定下来，前端在开发页面时就有明确的接口依据，可以减少前后端反复修改的成本。

下面给出 Cursor 的提示词模板：

````markdown
## 后端提示词

请为我开发一个基于 Node.js 和Express 框架的 Todo List 后端项目。项目需要实现以下四个 RESTful API 接口：

1. 查询所有待办事项
    - 接口名: GET /api/get-todo
    - 功能: 从数据库的'list'集合中查询并返回所有待办事项
    - 参数: 无
    - 返回: 包含所有待办事项的数组
2. 添加新的待办事项
    - 接口名: POST /api/add-todo
    - 功能: 向'list'集合中添加新的待办事项
    - 参数:
    {
    "value": string, // 待办事项的具体内容
    "isCompleted": boolean // 是否完成，默认为 false
    }
    - 返回: 新添加的待办事项对象，包含自动生成的唯一 id
3. 更新待办事项状态
    - 接口名: POST /api/update-todo/
    - 功能: 根据 id 更新指定待办事项的完成状态（将 isCompleted 值取反）
    - 参数: id
    - 返回: 更新后的待办事项对象
4. 删除待办事项
    - 接口名: POST /api/del-todo/
    - 功能: 根据 id 删除指定的待办事项
    - 参数: id
    - 返回: 删除操作的结果状态

技术要求：

1. 使用 Express 框架构建 API
2. 使用 MongoDB 作为数据库，通过 Mongoose 进行数据操作
3. 实现适当的错误处理和输入验证
4. 使用异步/等待（async/await）语法处理异步操作
5. 遵循 RESTful API 设计原则
6. 添加基本的日志记录功能

### 这里数据库连接方式要填写

以下是数据库连接方式：

1. 直接以当前目录作为项目根目录。注意：此目录已经初始化完 Node.js 项目，直接修改即可
2. 如果需要执行命令，请暂停创建文件，让我先执行命令

为这个项目中的所有代码写上详细注释

### 如果 npm 安装依赖较慢，可以先执行下面的命令

```jsx
npm config set registry https://registry.npmmirror.com
```

### 前端提示词

请为我开发一个基于 Vue 3 的Todo List 应用。要求如下：

1. 功能需求：
    - 添加新的待办事项
    - 标记待办事项为完成/未完成
    - 删除待办事项
    - 统计待办事项完成度
    - 过滤显示（全部/已完成/未完成）
2. UI/UX 设计要求：
    - 全屏响应式设计，适配不同设备
    - 拥有亮色模式和夜间模式
    - 现代化、简洁的界面风格
    - 丰富的色彩运用，但保持整体和谐
    - 流畅的交互动画，提升用户体验
    - 在按钮和需要的地方添加上图标
    - 参考灵感：结合苹果官网的设计美学

要求：

1. 直接以当前目录作为项目根目录。注意：此目录已经初始化完 Vue3 项目结构，直接修改即可
2. 如果需要执行命令，请暂停创建文件，让我先执行命令
3. 请你根据我的需求一步一步思考并开发这个项目，特别是 UI 部分，一定要足够美观和现代化

这里可以总结为：在前端开发阶段，我们主要通过 Cursor 发送提示词，清楚描述自己的需求、出现的问题，以及希望调整的功能和 UI 风格，再通过持续对话逐步完成页面开发和优化。
````

之后每个新增功能的流程基本都相同：先完成后端接口并测试保存，再将测试结果或测试用例交给前端，最后完成页面开发与接口对接。采用这种方式，可以让整个项目开发过程更加清晰，也更适合毕业设计这种“模块较多、需要快速推进”的项目场景。
