"""
Iris 数据导入模块。

这个文件负责项目中的数据准备层，不负责模型训练或评估。
当前实现同时覆盖两类数据来源：
1. 本地内置的 Iris 文本数据，便于离线开发和快速验证
2. 预留的数据库读取入口，便于后续替换为真实远程数据源

文件内的函数按职责拆分为三段：
1. 数据源接入：负责连接数据库或读取本地原始数据
2. 数据解析：负责把原始文本或查询结果整理成统一结构
3. 数据输出：负责向上层返回特征和标签，供模型模块直接使用
"""

from __future__ import annotations

import csv
import sqlite3
from io import StringIO
from typing import Any


IRIS_DATA = """
5.1,3.5,1.4,0.2,Iris-setosa
4.9,3.0,1.4,0.2,Iris-setosa
4.7,3.2,1.3,0.2,Iris-setosa
4.6,3.1,1.5,0.2,Iris-setosa
5.0,3.6,1.4,0.2,Iris-setosa
5.4,3.9,1.7,0.4,Iris-setosa
4.6,3.4,1.4,0.3,Iris-setosa
5.0,3.4,1.5,0.2,Iris-setosa
4.4,2.9,1.4,0.2,Iris-setosa
4.9,3.1,1.5,0.1,Iris-setosa
5.4,3.7,1.5,0.2,Iris-setosa
4.8,3.4,1.6,0.2,Iris-setosa
4.8,3.0,1.4,0.1,Iris-setosa
4.3,3.0,1.1,0.1,Iris-setosa
5.8,4.0,1.2,0.2,Iris-setosa
5.7,4.4,1.5,0.4,Iris-setosa
5.4,3.9,1.3,0.4,Iris-setosa
5.1,3.5,1.4,0.3,Iris-setosa
5.7,3.8,1.7,0.3,Iris-setosa
5.1,3.8,1.5,0.3,Iris-setosa
5.4,3.4,1.7,0.2,Iris-setosa
5.1,3.7,1.5,0.4,Iris-setosa
4.6,3.6,1.0,0.2,Iris-setosa
5.1,3.3,1.7,0.5,Iris-setosa
4.8,3.4,1.9,0.2,Iris-setosa
5.0,3.0,1.6,0.2,Iris-setosa
5.0,3.4,1.6,0.4,Iris-setosa
5.2,3.5,1.5,0.2,Iris-setosa
5.2,3.4,1.4,0.2,Iris-setosa
4.7,3.2,1.6,0.2,Iris-setosa
4.8,3.1,1.6,0.2,Iris-setosa
5.4,3.4,1.5,0.4,Iris-setosa
5.2,4.1,1.5,0.1,Iris-setosa
5.5,4.2,1.4,0.2,Iris-setosa
4.9,3.1,1.5,0.1,Iris-setosa
5.0,3.2,1.2,0.2,Iris-setosa
5.5,3.5,1.3,0.2,Iris-setosa
4.9,3.1,1.5,0.1,Iris-setosa
4.4,3.0,1.3,0.2,Iris-setosa
5.1,3.4,1.5,0.2,Iris-setosa
5.0,3.5,1.3,0.3,Iris-setosa
4.5,2.3,1.3,0.3,Iris-setosa
4.4,3.2,1.3,0.2,Iris-setosa
5.0,3.5,1.6,0.6,Iris-setosa
5.1,3.8,1.9,0.4,Iris-setosa
4.8,3.0,1.4,0.3,Iris-setosa
5.1,3.8,1.6,0.2,Iris-setosa
4.6,3.2,1.4,0.2,Iris-setosa
5.3,3.7,1.5,0.2,Iris-setosa
5.0,3.3,1.4,0.2,Iris-setosa
7.0,3.2,4.7,1.4,Iris-versicolor
6.4,3.2,4.5,1.5,Iris-versicolor
6.9,3.1,4.9,1.5,Iris-versicolor
5.5,2.3,4.0,1.3,Iris-versicolor
6.5,2.8,4.6,1.5,Iris-versicolor
5.7,2.8,4.5,1.3,Iris-versicolor
6.3,3.3,4.7,1.6,Iris-versicolor
4.9,2.4,3.3,1.0,Iris-versicolor
6.6,2.9,4.6,1.3,Iris-versicolor
5.2,2.7,3.9,1.4,Iris-versicolor
5.0,2.0,3.5,1.0,Iris-versicolor
5.9,3.0,4.2,1.5,Iris-versicolor
6.0,2.2,4.0,1.0,Iris-versicolor
6.1,2.9,4.7,1.4,Iris-versicolor
5.6,2.9,3.6,1.3,Iris-versicolor
6.7,3.1,4.4,1.4,Iris-versicolor
5.6,3.0,4.5,1.5,Iris-versicolor
5.8,2.7,4.1,1.0,Iris-versicolor
6.2,2.2,4.5,1.5,Iris-versicolor
5.6,2.5,3.9,1.1,Iris-versicolor
5.9,3.2,4.8,1.8,Iris-versicolor
6.1,2.8,4.0,1.3,Iris-versicolor
6.3,2.5,4.9,1.5,Iris-versicolor
6.1,2.8,4.7,1.2,Iris-versicolor
6.4,2.9,4.3,1.3,Iris-versicolor
6.6,3.0,4.4,1.4,Iris-versicolor
6.8,2.8,4.8,1.4,Iris-versicolor
6.7,3.0,5.0,1.7,Iris-versicolor
6.0,2.9,4.5,1.5,Iris-versicolor
5.7,2.6,3.5,1.0,Iris-versicolor
5.5,2.4,3.8,1.1,Iris-versicolor
5.5,2.4,3.7,1.0,Iris-versicolor
5.8,2.7,3.9,1.2,Iris-versicolor
6.0,2.7,5.1,1.6,Iris-versicolor
5.4,3.0,4.5,1.5,Iris-versicolor
6.0,3.4,4.5,1.6,Iris-versicolor
6.7,3.1,4.7,1.5,Iris-versicolor
6.3,2.3,4.4,1.3,Iris-versicolor
5.6,3.0,4.1,1.3,Iris-versicolor
5.5,2.5,4.0,1.3,Iris-versicolor
5.5,2.6,4.4,1.2,Iris-versicolor
6.1,3.0,4.6,1.4,Iris-versicolor
5.8,2.6,4.0,1.2,Iris-versicolor
5.0,2.3,3.3,1.0,Iris-versicolor
5.6,2.7,4.2,1.3,Iris-versicolor
5.7,3.0,4.2,1.2,Iris-versicolor
5.7,2.9,4.2,1.3,Iris-versicolor
6.2,2.9,4.3,1.3,Iris-versicolor
5.1,2.5,3.0,1.1,Iris-versicolor
5.7,2.8,4.1,1.3,Iris-versicolor
6.3,3.3,6.0,2.5,Iris-virginica
5.8,2.7,5.1,1.9,Iris-virginica
7.1,3.0,5.9,2.1,Iris-virginica
6.3,2.9,5.6,1.8,Iris-virginica
6.5,3.0,5.8,2.2,Iris-virginica
7.6,3.0,6.6,2.1,Iris-virginica
4.9,2.5,4.5,1.7,Iris-virginica
7.3,2.9,6.3,1.8,Iris-virginica
6.7,2.5,5.8,1.8,Iris-virginica
7.2,3.6,6.1,2.5,Iris-virginica
6.5,3.2,5.1,2.0,Iris-virginica
6.4,2.7,5.3,1.9,Iris-virginica
6.8,3.0,5.5,2.1,Iris-virginica
5.7,2.5,5.0,2.0,Iris-virginica
5.8,2.8,5.1,2.4,Iris-virginica
6.4,3.2,5.3,2.3,Iris-virginica
6.5,3.0,5.5,1.8,Iris-virginica
7.7,3.8,6.7,2.2,Iris-virginica
7.7,2.6,6.9,2.3,Iris-virginica
6.0,2.2,5.0,1.5,Iris-virginica
6.9,3.2,5.7,2.3,Iris-virginica
5.6,2.8,4.9,2.0,Iris-virginica
7.7,2.8,6.7,2.0,Iris-virginica
6.3,2.7,4.9,1.8,Iris-virginica
6.7,3.3,5.7,2.1,Iris-virginica
7.2,3.2,6.0,1.8,Iris-virginica
6.2,2.8,4.8,1.8,Iris-virginica
6.1,3.0,4.9,1.8,Iris-virginica
6.4,2.8,5.6,2.1,Iris-virginica
7.2,3.0,5.8,1.6,Iris-virginica
7.4,2.8,6.1,1.9,Iris-virginica
7.9,3.8,6.4,2.0,Iris-virginica
6.4,2.8,5.6,2.2,Iris-virginica
6.3,2.8,5.1,1.5,Iris-virginica
6.1,2.6,5.6,1.4,Iris-virginica
7.7,3.0,6.1,2.3,Iris-virginica
6.3,3.4,5.6,2.4,Iris-virginica
6.4,3.1,5.5,1.8,Iris-virginica
6.0,3.0,4.8,1.8,Iris-virginica
6.9,3.1,5.4,2.1,Iris-virginica
6.7,3.1,5.6,2.4,Iris-virginica
6.9,3.1,5.1,2.3,Iris-virginica
5.8,2.7,5.1,1.9,Iris-virginica
6.8,3.2,5.9,2.3,Iris-virginica
6.7,3.3,5.7,2.5,Iris-virginica
6.7,3.0,5.2,2.3,Iris-virginica
6.3,2.5,5.0,1.9,Iris-virginica
6.5,3.0,5.2,2.0,Iris-virginica
6.2,3.4,5.4,2.3,Iris-virginica
5.9,3.0,5.1,1.8,Iris-virginica
""".strip()


FEATURE_NAMES = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
]


DB_CONFIG = {
    "db_type": "sqlite",
    "database": "your_database.db",
    # "host": "127.0.0.1",
    # "port": 3306,
    # "user": "root",
    # "password": "your_password",
    # "database": "your_database_name",
}


def connect_db() -> sqlite3.Connection:
    """
    数据库连接入口。

    这个函数的实现思路是先根据配置判断数据库类型，再返回对应连接对象。
    当前仅保留 sqlite 占位实现，目的是让上层调用方式先固定下来；
    后续切换到 MySQL 或 PostgreSQL 时，只需要替换这里的连接细节。
    """
    db_type = DB_CONFIG.get("db_type")
    if db_type == "sqlite":
        return sqlite3.connect(DB_CONFIG["database"])

    raise NotImplementedError(
        f"暂未实现 {db_type} 的数据库连接，请在 connect_db() 中补充。"
    )


def fetch_data_from_db(sql: str, params: tuple[Any, ...] | None = None) -> list[tuple[Any, ...]]:
    """
    数据库查询入口。

    这个函数的实现思路是统一封装“连接、执行、取回、关闭”这一完整流程，
    让上层业务不直接依赖游标和连接对象。后续如果切到真实数据库，
    也可以继续复用这一调用模式。
    """
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        conn.close()


def parse_iris_text(raw_text: str) -> list[dict[str, Any]]:
    """
    将原始文本解析为结构化记录。

    这个函数的实现思路是逐行读取逗号分隔文本，再按字段位置映射成统一字典结构。
    这样无论数据来自硬编码文本、文件还是数据库导出内容，上层都能拿到相同格式的数据记录。
    """
    records: list[dict[str, Any]] = []
    reader = csv.reader(StringIO(raw_text.strip()))

    for row in reader:
        if not row:
            continue

        record = {
            "sepal_length": float(row[0]),
            "sepal_width": float(row[1]),
            "petal_length": float(row[2]),
            "petal_width": float(row[3]),
            "label": row[4],
        }
        records.append(record)

    return records


def load_local_dataset() -> list[dict[str, Any]]:
    """
    加载本地内置数据集。

    这个函数的实现思路是把“读取原始文本”和“调用解析逻辑”固定在一起，
    让调用方不关心底层数据是如何存放的，只拿到可直接使用的结构化结果。
    """
    return parse_iris_text(IRIS_DATA)


def load_dataset(source: str = "local") -> list[dict[str, Any]]:
    """
    统一数据导入入口。

    这个函数的实现思路是给模型层提供单一入口，通过 source 区分数据来源。
    当前默认走本地数据；如果未来切到数据库，只需要在这里扩展分支，
    模型层就不需要改动调用方式。
    """
    if source == "local":
        return load_local_dataset()

    if source == "db":
        raise NotImplementedError("数据库导入暂未启用，后续再接入真实数据库。")

    raise ValueError("source 仅支持 'local' 或 'db'")


def split_features_and_labels(
    records: list[dict[str, Any]],
) -> tuple[list[list[float]], list[str]]:
    """
    将结构化记录拆分为特征和标签。

    这个函数的实现思路是按固定字段顺序提取数值特征，并单独收集类别标签。
    这样模型模块就可以直接拿到训练所需的 X 和 y，不需要再理解底层记录结构。
    """
    features = [[record[name] for name in FEATURE_NAMES] for record in records]
    labels = [record["label"] for record in records]
    return features, labels


if __name__ == "__main__":
    dataset = load_dataset(source="local")
    features, labels = split_features_and_labels(dataset)

    print(f"成功导入 {len(dataset)} 条数据")
    print(f"特征维度: {len(features[0]) if features else 0}")
    print(f"类别示例: {sorted(set(labels))}")
    print("前 3 条记录:")
    for row in dataset[:3]:
        print(row)
