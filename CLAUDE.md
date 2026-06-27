# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

学生学业预警与成长分析平台 — 基于机器学习的智能预警系统，分析学生学业行为数据，识别潜在学业风险并提供个性化建议。课程设计项目（2026）。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（Flask 开发服务器，端口 5000）
python run.py

# 生成测试数据（可选）
python src/data_generator.py

# 运行学业预警分析（独立模块调用）
python -m src.academic_warning
```

LLM 功能需要本地 Ollama 服务运行在 `http://localhost:11434`，默认模型 `qwen2.5:7b`，配置见 `llm_config.json`。

## 架构

**后端**: Flask 单体应用，入口 `src/app.py`，通过 `run.py` 启动。
**前端**: 单页 `templates/index.html`，使用 Bootstrap + Chart.js。
**ML 管线**: scikit-learn 为主（决策树、逻辑回归、K-means、DBSCAN、Apriori），另有 PyTorch + PyG 用于 GNN 相关模块。

### 核心数据流

```
CSV 数据文件 (data/) 
  → data_processing/pipeline.py（加载→清洗→质量评估→特征工程）
  → classification/（风险分类模型训练与预测）
  → group_analysis/（聚类群体分析）
  → association_rules/（Apriori 关联规则挖掘）
  → learning_path_recommendation/（学习路径推荐）
  → report_generator/（报告生成，含 LLM 增强解释）
```

### 模块职责

| 模块 | 职责 |
|:---|:---|
| `src/app.py` | Flask 路由、文件上传、API 端点、会话管理 |
| `src/auth/` | 用户认证，支持 admin/teacher/student 三种角色 |
| `src/data_processing/` | 数据加载、清洗、特征工程、质量评估 |
| `src/classification/` | 决策树 + 逻辑回归风险分类器 |
| `src/group_analysis/` | K-means / DBSCAN 聚类分析 |
| `src/association_rules/` | Apriori 算法关联规则挖掘 |
| `src/learning_path_recommendation/` | 基于关联规则的学习路径推荐 |
| `src/report_generator/` | 报告生成（CSV + LLM 增强的自然语言解释） |
| `src/llm_integration/` | OpenAI 协议客户端，对接本地 Ollama |
| `src/student_behavior_representation/` | SimCLR 行为表征、数据增强、时序对齐 |
| `src/gnn_explanation/` | GNN 模型与解释器 |
| `src/academic_warning.py` | 预警主程序入口 + 高级数据生成器 |

### 关键文件

- `data/` — 四个核心 CSV：`students.csv`、`grades.csv`、`attendance.csv`、`courses.csv`
- `advanced_data/` — 增强数据（含 CSV/JSON/Parquet 格式）
- `reports/` — 生成的报告、图表、通知日志
- `templates/index.html` — 前端单页（包含所有页面视图和 JS 逻辑）
- `llm_config.json` — LLM 服务配置

## 注意事项

- 模块间通过 `from src.xxx import ...` 交叉引用，需确保 `src/` 在 Python 路径中（`run.py` 已处理）
- 预警系统通过 `subprocess` 调用 `python -m src.academic_warning`，非直接函数调用
- 前端认证凭证硬编码（admin/admin123、teacher/teacher123、student/student123）
- PyTorch 依赖为 CPU 版本（`+cpu`），不使用 GPU
