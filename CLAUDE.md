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

# 运行测试
pytest tests/ -v

# 运行学业预警分析（独立模块调用）
python -m src.academic_warning
```

LLM 功能需要本地 Ollama 服务运行在 `http://localhost:11434`，默认模型 `qwen2.5:7b`，配置见 `llm_config.json`。

## 架构

**后端**: Flask 工厂模式 + Blueprint 架构，入口 `run.py` → `src/app.py`（create_app 工厂）。
**前端**: 单页 `templates/index.html`，Bootstrap 5 + Bootstrap Icons + Chart.js。
**ML 管线**: scikit-learn 为主（决策树、逻辑回归、K-means、DBSCAN、Apriori），另有 PyTorch + PyG 用于 GNN 相关模块（可选安装）。

### Blueprint 路由组织

| Blueprint | 文件 | URL 前缀 | 职责 |
|:---|:---|:---|:---|
| `auth_bp` | `src/blueprints/auth_bp.py` | `/api` | 登录、登出、用户管理 |
| `data_bp` | `src/blueprints/data_bp.py` | `/` | 首页、文件上传、模板下载 |
| `warning_bp` | `src/blueprints/warning_bp.py` | `/` | 预警执行、报告查询、通知发送 |
| `analysis_bp` | `src/blueprints/analysis_bp.py` | `/` | 群体分析、学习路径、行为分析 |
| `report_bp` | `src/blueprints/report_bp.py` | `/` | 报告生成 |
| `llm_bp` | `src/blueprints/llm_bp.py` | `/` | LLM 配置与调用 |

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
| `src/app.py` | Flask 工厂（create_app），注册 Blueprint |
| `src/blueprints/` | 6 个 Blueprint 路由模块 |
| `src/core/decorators.py` | `@login_required`、`@role_required` 认证装饰器 |
| `src/auth/` | 用户认证，werkzeug 密码哈希，TOTP 2FA |
| `src/data_processing/` | 数据加载、清洗、特征工程、质量评估 |
| `src/classification/` | 决策树 + 逻辑回归风险分类器 |
| `src/group_analysis/` | K-means / DBSCAN 聚类分析 |
| `src/association_rules/` | Apriori 算法关联规则挖掘 |
| `src/learning_path_recommendation/` | 基于关联规则的学习路径推荐 |
| `src/report_generator/` | 报告生成（CSV + LLM 增强） |
| `src/llm_integration/` | OpenAI 协议客户端，对接本地 Ollama |
| `src/student_behavior_representation/` | SimCLR 行为表征 |
| `src/gnn_explanation/` | GNN 模型与解释器 |
| `src/academic_warning.py` | 预警主程序 + 数据生成器 |

### 关键文件

- `data/` — 四个核心 CSV：`students.csv`（含 gender 列）、`grades.csv`、`attendance.csv`、`courses.csv`
- `templates/index.html` — 前端单页（4800+ 行，含所有页面视图和 JS 逻辑）
- `llm_config.json` — LLM 服务配置
- `instance/auth/` — 运行时用户数据（.gitignore 排除）

## 注意事项

- 所有模块统一使用 `from src.xxx import ...` 导入路径
- 认证装饰器在 `src/core/decorators.py`，Blueprint 中使用 `@login_required` 和 `@role_required('admin')`
- 预警系统通过 `subprocess` 调用 `python -m src.academic_warning`，非直接函数调用
- 默认管理员账户：admin / Admin@123（教师/学生账户需管理员创建）
- PyTorch 为可选依赖，需单独安装（CPU 版本）
- 运行时数据存储在 `instance/auth/`，已从源码目录分离
