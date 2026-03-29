"""
Iris 训练服务后端。

这个文件是训练服务的主入口，负责把“数据库取数、模型训练、指标计算、科研风格绘图、
静态资源暴露、预测接口”整合为一个可供前端调用的 HTTP API。

整体实现可以分为五层：
1. 配置与请求模型：定义可选超参数、默认值和接口入参结构
2. 数据访问层：负责连接 MySQL 并把查询结果整理成训练可用格式
3. 模型与评估层：负责 PyTorch 训练、混淆矩阵与分类指标计算
4. 绘图层：负责生成符合科研展示习惯的高分辨率静态图像
5. API 层：负责提交训练任务、查询结果、返回图片地址和执行单样本预测
"""

from __future__ import annotations

import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import numpy as np
import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

HIDDEN_DIM_OPTIONS = [4, 8, 12, 16]
EPOCH_OPTIONS = [20, 50, 100]
BATCH_SIZE_OPTIONS = [4, 8, 16]
LEARNING_RATE_OPTIONS = [0.001, 0.005, 0.01]
OPTIMIZER_OPTIONS = ["adam", "sgd"]
ACTIVATION_OPTIONS = ["sigmoid", "relu"]


def _parse_mysql_url(db_url: str) -> dict[str, Any]:
    """
    解析 MySQL 连接串。

    这个函数的实现思路是把外部配置的数据库 URL 统一拆解成 PyMySQL 所需参数，
    这样调用方只需要维护一个连接串，而不需要在各处重复处理 host、port 和数据库名。
    """
    parsed = urlparse(db_url)
    if parsed.scheme != "mysql":
        raise ValueError("DB_URL must start with mysql://")
    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": parsed.username,
        "password": parsed.password,
        "database": (parsed.path or "/").lstrip("/") or "iris_db",
        "charset": "utf8mb4",
        "connect_timeout": 10,
    }


DB_URL = os.getenv(
    "DB_URL",
    "mysql://root:qtrvvcdr@test-db-mysql.ns-3448g4cy.svc:3306/iris_db",
)
DEFAULT_QUERY = (
    "SELECT sepal_length, sepal_width, petal_length, petal_width, class AS label FROM iris"
)
BASE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = BASE_DIR / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class TrainParams(BaseModel):
    hidden_dim: Literal[4, 8, 12, 16] = 8
    epochs: Literal[20, 50, 100] = 50
    batch_size: Literal[4, 8, 16] = 8
    learning_rate: Literal[0.001, 0.005, 0.01] = 0.001
    optimizer: Literal["adam", "sgd"] = "adam"
    activation: Literal["sigmoid", "relu"] = "relu"
    test_size: float = 0.2
    val_size: float = 0.2
    random_state: int = 42


class CreateTrainJobReq(BaseModel):
    db_query: str = DEFAULT_QUERY
    label_column: str = "label"
    feature_columns: list[str] = Field(
        default_factory=lambda: [
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
        ]
    )
    params: TrainParams = TrainParams()


class PredictReq(BaseModel):
    features: list[float]
    job_id: str | None = None


@dataclass
class ModelBundle:
    model: Any
    scaler: StandardScaler
    label_encoder: LabelEncoder
    params: dict[str, Any]


app = FastAPI(title="Iris Training API", version="1.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/artifacts", StaticFiles(directory=str(ARTIFACT_DIR)), name="artifacts")

executor = ThreadPoolExecutor(max_workers=2)
store_lock = threading.Lock()
jobs: dict[str, dict[str, Any]] = {}
models: dict[str, ModelBundle] = {}


def _get_conn() -> pymysql.connections.Connection:
    """
    创建数据库连接。

    这个函数的实现思路是把数据库连接动作统一收敛到一个小入口，
    上层训练逻辑只依赖“拿到连接”这件事，不直接关心 URL 解析和驱动细节。
    """
    return pymysql.connect(**_parse_mysql_url(DB_URL))


def _fetch_records(
    query: str, feature_columns: list[str], label_column: str
) -> tuple[np.ndarray, np.ndarray]:
    """
    从数据库取回训练记录并整理成特征数组与标签数组。

    这个函数的实现思路是先执行查询，再根据列名做字段映射和类型清洗，
    统一输出 numpy 格式的 X、y。这样后续训练代码不必理解数据库行结构，
    只处理标准化后的数值输入。
    """
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
    finally:
        conn.close()

    if not rows:
        raise ValueError("database query returned empty result")

    col_idx = {col: idx for idx, col in enumerate(columns)}
    missing = [col for col in (feature_columns + [label_column]) if col not in col_idx]
    if missing:
        raise ValueError(f"missing columns in query result: {missing}")

    x: list[list[float]] = []
    y: list[str] = []
    for row in rows:
        feature_row: list[float] = []
        for col in feature_columns:
            value = row[col_idx[col]]
            if isinstance(value, Decimal):
                value = float(value)
            feature_row.append(float(value))
        x.append(feature_row)
        y.append(str(row[col_idx[label_column]]))

    return np.asarray(x, dtype=np.float32), np.asarray(y, dtype=object)


def _build_activation(name: str) -> Any:
    """
    根据配置构建激活函数层。

    这个函数的实现思路是把可选激活函数集中管理，
    让训练主流程只处理配置选择，不把具体层实现散落在网络构建代码里。
    """
    import torch.nn as nn

    if name == "relu":
        return nn.ReLU()
    if name == "sigmoid":
        return nn.Sigmoid()
    raise ValueError(f"unsupported activation: {name}")


def _build_optimizer(name: str, model: Any, learning_rate: float) -> Any:
    """
    根据配置构建优化器。

    这个函数的实现思路是把优化器选择逻辑独立出来，
    让请求参数与训练实现之间保持清晰映射，后续扩展其他优化器也更直接。
    """
    import torch.optim as optim

    if name == "adam":
        return optim.Adam(model.parameters(), lr=learning_rate)
    if name == "sgd":
        return optim.SGD(model.parameters(), lr=learning_rate)
    raise ValueError(f"unsupported optimizer: {name}")


def _build_confusion_stats(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
) -> dict[str, Any]:
    """
    基于预测结果生成混淆矩阵和每类 TP/FP/TN/FN。

    这个函数的实现思路是先生成标准混淆矩阵，再按 one-vs-rest 方式
    为每个类别计算基础分类统计量。这样既保留了原始矩阵，
    也提供了便于下游分析的基础计数结果。
    """
    matrix = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    total = int(matrix.sum())
    per_class: dict[str, dict[str, int]] = {}

    for idx, class_name in enumerate(class_names):
        tp = int(matrix[idx, idx])
        fp = int(matrix[:, idx].sum() - tp)
        fn = int(matrix[idx, :].sum() - tp)
        tn = int(total - tp - fp - fn)
        per_class[class_name] = {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
        }

    return {
        "labels": class_names,
        "matrix": matrix.tolist(),
        "per_class": per_class,
    }


def _build_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
) -> tuple[dict[str, float], dict[str, dict[str, float | int]]]:
    """
    计算总体与分类别评估指标。

    这个函数的实现思路是同时输出两套指标：
    一套是宏平均 precision、recall、f1，用于结果总览；
    一套是分类别 precision、recall、f1、support，用于细粒度分析和论文表格展示。
    """
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0,
    )

    precisions, recalls, f1_scores, supports = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        average=None,
        zero_division=0,
    )

    per_class_metrics: dict[str, dict[str, float | int]] = {}
    for idx, class_name in enumerate(class_names):
        per_class_metrics[class_name] = {
            "precision": float(precisions[idx]),
            "recall": float(recalls[idx]),
            "f1": float(f1_scores[idx]),
            "support": int(supports[idx]),
        }

    return (
        {
            "macro_precision": float(macro_precision),
            "macro_recall": float(macro_recall),
            "macro_f1": float(macro_f1),
        },
        per_class_metrics,
    )


def _configure_plot_style() -> None:
    """
    配置统一的科研绘图风格。

    这个函数的实现思路是集中设置分辨率、字体、边框和字号，
    保证所有导出的图在风格上保持一致，并尽量贴近论文图表对清晰度和规范性的要求。
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "font.family": "DejaVu Serif",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
        }
    )


def _save_training_plots(
    job_id: str,
    history: dict[str, list[float]],
    confusion: dict[str, Any],
    per_class_metrics: dict[str, dict[str, float | int]],
) -> dict[str, str]:
    """
    生成训练结果图并保存为静态文件。

    这个函数的实现思路是把训练过程中的数值结果转换成可直接展示的高分辨率 PNG，
    包括损失曲线、准确率曲线、混淆矩阵和分类别指标图。函数最终返回静态资源 URL，
    让前端只做图片展示，不承担核心评估图绘制逻辑。
    """
    _configure_plot_style()
    import matplotlib.pyplot as plt

    job_dir = ARTIFACT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    epochs = np.arange(1, len(history["train_loss"]) + 1)

    loss_path = job_dir / "loss_curve.png"
    plt.figure(figsize=(6.4, 4.8))
    plt.plot(epochs, history["train_loss"], color="#1f3a5f", linewidth=2.0, label="Train Loss")
    plt.plot(epochs, history["val_loss"], color="#b24c3d", linewidth=2.0, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(loss_path, bbox_inches="tight")
    plt.close()

    acc_path = job_dir / "accuracy_curve.png"
    plt.figure(figsize=(6.4, 4.8))
    plt.plot(epochs, history["train_acc"], color="#1f3a5f", linewidth=2.0, label="Train Accuracy")
    plt.plot(epochs, history["val_acc"], color="#2d6a4f", linewidth=2.0, label="Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Training and Validation Accuracy")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(acc_path, bbox_inches="tight")
    plt.close()

    matrix = np.asarray(confusion["matrix"], dtype=float)
    labels = confusion["labels"]
    cm_path = job_dir / "confusion_matrix.png"
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    image = ax.imshow(matrix, cmap="Blues", aspect="equal")
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Count", rotation=270, labelpad=15)
    ax.set_xticks(np.arange(len(labels)), labels=labels, rotation=15, ha="right")
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_title("Confusion Matrix")
    max_value = matrix.max() if matrix.size else 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            color = "white" if matrix[i, j] > max_value * 0.5 else "#1a1a1a"
            ax.text(j, i, int(matrix[i, j]), ha="center", va="center", color=color)
    fig.tight_layout()
    fig.savefig(cm_path, bbox_inches="tight")
    plt.close(fig)

    class_names = list(per_class_metrics.keys())
    precision_values = [float(per_class_metrics[name]["precision"]) for name in class_names]
    recall_values = [float(per_class_metrics[name]["recall"]) for name in class_names]
    f1_values = [float(per_class_metrics[name]["f1"]) for name in class_names]
    x = np.arange(len(class_names))
    width = 0.22

    metrics_path = job_dir / "per_class_metrics.png"
    plt.figure(figsize=(7.2, 4.8))
    plt.bar(x - width, precision_values, width=width, color="#355070", label="Precision")
    plt.bar(x, recall_values, width=width, color="#6d597a", label="Recall")
    plt.bar(x + width, f1_values, width=width, color="#b56576", label="F1")
    plt.xticks(x, class_names, rotation=15, ha="right")
    plt.ylim(0, 1.05)
    plt.ylabel("Score")
    plt.title("Per-class Evaluation Metrics")
    plt.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.35)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(metrics_path, bbox_inches="tight")
    plt.close()

    return {
        "loss_curve_url": f"/artifacts/{job_id}/loss_curve.png",
        "accuracy_curve_url": f"/artifacts/{job_id}/accuracy_curve.png",
        "confusion_matrix_url": f"/artifacts/{job_id}/confusion_matrix.png",
        "per_class_metrics_url": f"/artifacts/{job_id}/per_class_metrics.png",
    }


def _run_train_job(job_id: str, req: CreateTrainJobReq) -> None:
    """
    在后台线程中执行完整训练任务。

    这个函数的实现思路是把一次训练任务拆成标准实验流程：
    取数、编码、划分数据集、标准化、训练、验证、测试、评估、绘图、入库结果。
    由于训练过程可能较长，这里使用任务状态表配合后台线程，
    让前端通过轮询接口观察进度而不是阻塞等待。
    """
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ModuleNotFoundError:
        with store_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "torch is not installed"
        return

    with store_lock:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["progress"] = 0.01

    try:
        x, y_text = _fetch_records(req.db_query, req.feature_columns, req.label_column)
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y_text)

        x_train_all, x_test, y_train_all, y_test = train_test_split(
            x,
            y,
            test_size=req.params.test_size,
            random_state=req.params.random_state,
            stratify=y,
        )
        x_train, x_val, y_train, y_val = train_test_split(
            x_train_all,
            y_train_all,
            test_size=req.params.val_size,
            random_state=req.params.random_state,
            stratify=y_train_all,
        )

        scaler = StandardScaler()
        x_train = scaler.fit_transform(x_train)
        x_val = scaler.transform(x_val)
        x_test = scaler.transform(x_test)

        x_train_t = torch.tensor(x_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.long)
        x_val_t = torch.tensor(x_val, dtype=torch.float32)
        y_val_t = torch.tensor(y_val, dtype=torch.long)
        x_test_t = torch.tensor(x_test, dtype=torch.float32)
        y_test_t = torch.tensor(y_test, dtype=torch.long)

        train_loader = DataLoader(
            TensorDataset(x_train_t, y_train_t),
            batch_size=req.params.batch_size,
            shuffle=True,
        )

        model = nn.Sequential(
            nn.Linear(x.shape[1], req.params.hidden_dim),
            _build_activation(req.params.activation),
            nn.Linear(req.params.hidden_dim, len(label_encoder.classes_)),
        )

        criterion = nn.CrossEntropyLoss()
        optimizer = _build_optimizer(
            req.params.optimizer,
            model,
            req.params.learning_rate,
        )
        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

        for epoch in range(req.params.epochs):
            model.train()
            total_loss = 0.0
            correct = 0
            total = 0

            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                logits = model(batch_x)
                loss = criterion(logits, batch_y)
                loss.backward()
                optimizer.step()

                total_loss += loss.item() * batch_x.size(0)
                preds = torch.argmax(logits, dim=1)
                correct += (preds == batch_y).sum().item()
                total += batch_y.size(0)

            model.eval()
            with torch.no_grad():
                val_logits = model(x_val_t)
                val_loss = criterion(val_logits, y_val_t).item()
                val_preds = torch.argmax(val_logits, dim=1)
                val_acc = (val_preds == y_val_t).float().mean().item()

            history["train_loss"].append(float(total_loss / total))
            history["train_acc"].append(float(correct / total))
            history["val_loss"].append(float(val_loss))
            history["val_acc"].append(float(val_acc))

            with store_lock:
                jobs[job_id]["progress"] = round((epoch + 1) / req.params.epochs, 4)
                jobs[job_id]["current_epoch"] = epoch + 1

        model.eval()
        with torch.no_grad():
            test_logits = model(x_test_t)
            test_loss = criterion(test_logits, y_test_t).item()
            pred_classes_t = torch.argmax(test_logits, dim=1)
            test_acc = (pred_classes_t == y_test_t).float().mean().item()
            pred_probs = torch.softmax(test_logits, dim=1).numpy()

        pred_classes = pred_classes_t.numpy()
        class_names = label_encoder.classes_.tolist()
        confusion = _build_confusion_stats(y_test, pred_classes, class_names)
        summary_metrics, per_class_metrics = _build_classification_metrics(
            y_test,
            pred_classes,
            class_names,
        )
        selected_params = req.params.model_dump()
        plots = _save_training_plots(
            job_id,
            history,
            confusion,
            per_class_metrics,
        )

        with store_lock:
            models[job_id] = ModelBundle(
                model=model,
                scaler=scaler,
                label_encoder=label_encoder,
                params=selected_params,
            )
            jobs[job_id]["status"] = "succeeded"
            jobs[job_id]["result"] = {
                "selected_params": selected_params,
                "metrics": {
                    "test_loss": float(test_loss),
                    "test_accuracy": float(test_acc),
                    **summary_metrics,
                },
                "class_names": class_names,
                "history": history,
                "confusion": confusion,
                "per_class_metrics": per_class_metrics,
                "plots": plots,
                "sample_predictions": {
                    "y_true": y_test[:10].tolist(),
                    "y_pred": pred_classes[:10].tolist(),
                    "probs": pred_probs[:10].tolist(),
                },
                "data_summary": {"rows": int(x.shape[0]), "feature_dim": int(x.shape[1])},
            }
    except Exception as exc:
        with store_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(exc)


@app.get("/health")
def health() -> dict[str, str]:
    """
    服务健康检查接口。

    这个接口的实现思路是返回最小可用响应，
    用于前端或网关确认训练服务进程是否存活。
    """
    return {"status": "ok"}


@app.get("/api/v1/train/options")
def get_train_options() -> dict[str, Any]:
    """
    返回训练页所需的超参数选项。

    这个接口的实现思路是由后端统一定义默认值、可选枚举和值域，
    避免前端写死训练配置，保证页面展示与后端实际支持的参数保持一致。
    """
    return {
        "defaults": {
            "hidden_dim": 8,
            "epochs": 50,
            "batch_size": 8,
            "learning_rate": 0.001,
            "optimizer": "adam",
            "activation": "relu",
        },
        "options": {
            "hidden_dim": HIDDEN_DIM_OPTIONS,
            "epochs": EPOCH_OPTIONS,
            "batch_size": BATCH_SIZE_OPTIONS,
            "learning_rate": LEARNING_RATE_OPTIONS,
            "optimizer": OPTIMIZER_OPTIONS,
            "activation": ACTIVATION_OPTIONS,
        },
        "fixed_params": {
            "test_size": 0.2,
            "val_size": 0.2,
            "random_state": 42,
        },
    }


@app.post("/api/v1/train/jobs")
def create_train_job(req: CreateTrainJobReq) -> dict[str, Any]:
    """
    创建训练任务。

    这个接口的实现思路是先生成任务 ID 并写入初始状态，
    再把真实训练过程提交到后台线程执行。接口本身只返回任务受理结果，
    由前端后续通过轮询接口继续追踪进度。
    """
    job_id = f"train_{uuid.uuid4().hex[:10]}"
    with store_lock:
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0.0,
            "current_epoch": 0,
            "total_epochs": req.params.epochs,
            "error": None,
            "result": None,
        }
    executor.submit(_run_train_job, job_id, req)
    return {
        "job_id": job_id,
        "status": "queued",
        "selected_params": req.params.model_dump(),
    }


@app.get("/api/v1/train/jobs/{job_id}")
def get_train_job(job_id: str) -> dict[str, Any]:
    """
    查询训练任务进度。

    这个接口的实现思路是只返回任务状态、进度和错误信息，
    让前端可以轻量轮询，而不需要在训练未完成时反复取回完整结果。
    """
    with store_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job["progress"],
            "current_epoch": job["current_epoch"],
            "total_epochs": job["total_epochs"],
            "error": job["error"],
        }


@app.get("/api/v1/train/jobs/{job_id}/result")
def get_train_result(job_id: str) -> dict[str, Any]:
    """
    查询训练结果。

    这个接口的实现思路是根据任务状态决定返回结构：
    如果任务尚未完成，只返回当前状态；如果训练成功，
    则一次性返回指标、图像地址、混淆矩阵和分类别结果，供前端完整展示。
    """
    with store_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        if job["status"] != "succeeded":
            return {"job_id": job_id, "status": job["status"], "error": job["error"]}
        return {"job_id": job_id, "status": "succeeded", **job["result"]}


@app.post("/api/v1/predict")
def predict(req: PredictReq) -> dict[str, Any]:
    """
    执行单样本预测。

    这个接口的实现思路是优先定位指定任务对应的已训练模型，
    若前端未指定 job_id，则默认使用最近一次成功训练的模型。
    随后沿用训练阶段保存的 scaler 和标签编码器，保证预测口径与训练保持一致。
    """
    with store_lock:
        if not models:
            raise HTTPException(status_code=400, detail="no trained model available")
        if req.job_id:
            bundle = models.get(req.job_id)
            if not bundle:
                raise HTTPException(status_code=404, detail="model for job_id not found")
        else:
            bundle = models[next(reversed(models.keys()))]

    try:
        import torch
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=500, detail=f"missing dependency: {exc.name}")

    x = np.asarray([req.features], dtype=np.float32)
    x_scaled = bundle.scaler.transform(x)
    x_t = torch.tensor(x_scaled, dtype=torch.float32)

    bundle.model.eval()
    with torch.no_grad():
        logits = bundle.model(x_t)
        probs = torch.softmax(logits, dim=1).numpy()[0]

    pred_idx = int(np.argmax(probs))
    pred_label = bundle.label_encoder.classes_[pred_idx]
    return {
        "pred_class": str(pred_label),
        "pred_index": pred_idx,
        "probabilities": probs.tolist(),
        "selected_params": bundle.params,
    }
