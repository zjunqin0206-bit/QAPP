"""
Iris 分类模型模块。

这个文件负责训练、评估和预测流程，不负责底层数据采集。
整体结构遵循“数据准备 -> 模型构建 -> 训练评估 -> 结果输出”的顺序，
便于后续把本地数据源替换成数据库数据源，而不改动模型主流程。

当前实现基于 PyTorch 完成一个轻量级三分类网络，
适合作为本地原型验证与后续服务化改造的基础版本。
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from data import load_dataset, split_features_and_labels


def prepare_training_data(source: str = "local") -> tuple[list[list[float]], list[str]]:
    """
    加载并整理训练数据。

    这个函数的实现思路是把模型层与数据层隔离开：
    模型只关心训练所需的特征和标签，不直接依赖数据源细节，
    因而后续无论切换本地数据还是数据库数据，调用方式都保持一致。
    """
    dataset = load_dataset(source=source)
    return split_features_and_labels(dataset)


def build_model(input_dim: int, num_classes: int) -> Any:
    """
    构建 PyTorch 分类模型。

    这个函数的实现思路是把网络结构单独抽离出来，
    让训练流程只负责调用，不混入网络定义细节。
    当前采用单隐藏层结构，既能满足 Iris 任务复杂度，
    也便于后续替换层数、节点数和激活函数。
    """
    import torch.nn as nn

    model = nn.Sequential(
        nn.Linear(input_dim, 8),
        nn.ReLU(),
        nn.Linear(8, num_classes),
    )
    return model


def plot_training_curves(history: dict[str, list[float]], output_dir: str = ".") -> tuple[str | None, str | None]:
    """
    绘制并保存训练曲线。

    这个函数的实现思路是把训练日志转换为离线图片文件，
    避免把绘图逻辑散落在主训练流程中。函数同时兼容缺少 matplotlib 的环境：
    当依赖不可用时直接跳过绘图，保证训练流程本身不被阻断。
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return None, None

    loss_path = f"{output_dir}/training_loss.png"
    acc_path = f"{output_dir}/training_accuracy.png"

    plt.figure()
    plt.plot(history["train_loss"], label="train_loss")
    plt.plot(history["val_loss"], label="val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.title("Training and Validation Loss")
    plt.tight_layout()
    plt.savefig(loss_path, dpi=150)
    plt.close()

    plt.figure()
    plt.plot(history["train_acc"], label="train_acc")
    plt.plot(history["val_acc"], label="val_acc")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.title("Training and Validation Accuracy")
    plt.tight_layout()
    plt.savefig(acc_path, dpi=150)
    plt.close()

    return loss_path, acc_path


def train_and_evaluate(source: str = "local") -> dict[str, Any]:
    """
    完成训练、评估与示例预测。

    这个函数的实现思路是把完整实验流程串成一个闭环：
    先完成数据拆分与标准化，再执行训练和验证，
    随后在测试集上评估，并补充一个单样本预测示例。
    最终统一返回结构化结果，便于命令行展示或后续接口化封装。
    """
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    features, labels = prepare_training_data(source=source)
    x = np.asarray(features, dtype=np.float32)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    x_train, x_val, y_train, y_val = train_test_split(
        x_train,
        y_train,
        test_size=0.2,
        random_state=42,
        stratify=y_train,
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
        batch_size=8,
        shuffle=True,
    )

    model = build_model(input_dim=x.shape[1], num_classes=len(label_encoder.classes_))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 50
    history = {
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
    }

    for _ in range(epochs):
        model.train()
        train_loss_sum = 0.0
        train_correct = 0
        train_total = 0

        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            train_loss_sum += loss.item() * batch_x.size(0)
            preds = torch.argmax(logits, dim=1)
            train_correct += (preds == batch_y).sum().item()
            train_total += batch_y.size(0)

        model.eval()
        with torch.no_grad():
            val_logits = model(x_val_t)
            val_loss = criterion(val_logits, y_val_t).item()
            val_preds = torch.argmax(val_logits, dim=1)
            val_acc = (val_preds == y_val_t).float().mean().item()

        train_loss = train_loss_sum / train_total
        train_acc = train_correct / train_total

        history["train_loss"].append(float(train_loss))
        history["val_loss"].append(float(val_loss))
        history["train_acc"].append(float(train_acc))
        history["val_acc"].append(float(val_acc))

    model.eval()
    with torch.no_grad():
        test_logits = model(x_test_t)
        test_loss = criterion(test_logits, y_test_t).item()
        pred_classes_t = torch.argmax(test_logits, dim=1)
        test_acc = (pred_classes_t == y_test_t).float().mean().item()
        pred_probs = torch.softmax(test_logits, dim=1).numpy()
        pred_classes = pred_classes_t.numpy()

    new_sample = np.asarray([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
    new_sample_scaled = scaler.transform(new_sample)
    new_sample_t = torch.tensor(new_sample_scaled, dtype=torch.float32)
    with torch.no_grad():
        new_logits = model(new_sample_t)
        new_pred_prob = torch.softmax(new_logits, dim=1).numpy()
        new_pred_class = int(np.argmax(new_pred_prob, axis=1)[0])

    loss_plot_path, acc_plot_path = plot_training_curves(history, output_dir=".")

    return {
        "test_loss": float(test_loss),
        "test_acc": float(test_acc),
        "pred_classes_first10": pred_classes[:10].tolist(),
        "y_test_first10": y_test[:10].tolist(),
        "new_sample_prediction_prob": new_pred_prob.tolist(),
        "new_sample_prediction_label": label_encoder.classes_[new_pred_class],
        "class_names": label_encoder.classes_.tolist(),
        "loss_plot_path": loss_plot_path,
        "acc_plot_path": acc_plot_path,
    }


if __name__ == "__main__":
    try:
        result = train_and_evaluate(source="local")
    except ModuleNotFoundError as exc:
        print(f"缺少依赖: {exc.name}")
        print("请先安装依赖后再运行:")
        print("pip install torch matplotlib scikit-learn numpy")
    else:
        print("测试集损失:", result["test_loss"])
        print("测试集准确率:", result["test_acc"])
        print("前10个预测类别:", result["pred_classes_first10"])
        print("前10个真实类别:", result["y_test_first10"])
        print("新样本预测概率:", result["new_sample_prediction_prob"])
        print("新样本预测类别:", result["new_sample_prediction_label"])
        print("类别名称:", result["class_names"])
        if result["loss_plot_path"] and result["acc_plot_path"]:
            print("损失曲线图:", result["loss_plot_path"])
            print("准确率曲线图:", result["acc_plot_path"])
        else:
            print("未生成训练曲线图（缺少 matplotlib）")
