# 学生学业预警与成长分析平台

## 项目简介

学生学业预警与成长分析平台是一个基于机器学习算法的智能预警系统，旨在通过分析学生的学业行为数据，提前识别潜在的学业风险，并提供个性化的学习建议和成长分析。

## 功能特点

- **智能预警**：基于决策树和逻辑回归算法，识别高风险学生
- **群体分析**：使用K-means和DBSCAN聚类算法进行学生群体特征发现
- **学习路径推荐**：基于Apriori关联规则算法，推荐个性化学习路径
- **数据可视化**：提供直观的风险分布、特征重要性等数据可视化展示
- **批量预警**：支持批量选择和发送预警通知给教师和学生
- **数据导入导出**：支持CSV格式数据的导入和报告导出

## 系统架构

- **前端**：HTML、CSS、JavaScript、Bootstrap、Chart.js
- **后端**：Flask框架
- **数据处理**：Pandas、NumPy
- **机器学习**：scikit-learn（决策树、逻辑回归、K-means、DBSCAN、Apriori）
- **数据可视化**：Matplotlib、Seaborn、Chart.js

## 安装步骤

1. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

2. **生成测试数据**（可选）
   ```bash
   python data_generator.py
   ```

3. **启动服务**
   ```bash
   python run.py
   ```

4. **访问系统**
   在浏览器中打开：http://127.0.0.1:5000

## 系统使用说明

### 1. 登录系统

系统支持三种角色登录：
- **管理员**：用户名 `admin`，密码 `admin123`
- **教师**：用户名 `teacher`，密码 `teacher123`
- **学生**：用户名 `student`，密码 `student123`

### 2. 数据管理（仅管理员）

1. **上传数据文件**
   - 在左侧菜单栏点击"数据管理"
   - 上传以下CSV格式的文件：
     - `students.csv` - 学生基本信息
     - `grades.csv` - 学生成绩数据
     - `attendance.csv` - 学生出勤记录
     - `courses.csv` - 学生选课行为

2. **下载数据模板**
   - 点击相应的"下载"按钮获取数据导入模板

3. **运行预警系统**
   - 点击"运行预警系统"按钮，系统将分析数据并生成预警报告

### 3. 学业预警

1. **查看预警学生列表**
   - 在左侧菜单栏点击"学业预警"
   - 系统会显示所有有风险的学生（高风险、中风险、低风险）

2. **查看学生详情**
   - 点击学生列表中的"详情"按钮查看详细信息

3. **发送预警通知**
   - 单个预警：点击"预警"按钮向单个学生发送预警
   - 批量预警：
     - 使用复选框选择多个学生
     - 点击"批量预警"按钮
     - 确认后系统会向选中的学生发送预警通知，同时教师端也会收到通知

### 4. 群体分析

1. **查看群体特征**
   - 在左侧菜单栏点击"群体分析"
   - 系统会显示不同群体的特征分析，包括：
     - 群体大小分布
     - 群体成绩分布
     - 群体出勤率分布
     - 群体特征详细信息

2. **群体代码含义**
   - 行为模式分类：高风险行为、中等风险行为、低风险行为、正常
   - 风险因素说明：挂科门数过多、平均成绩过低、成绩波动较大、出勤率过低等

### 5. 学习路径推荐

1. **获取推荐课程**
   - 在左侧菜单栏点击"学习路径推荐"
   - 输入学生ID
   - 点击"获取推荐"按钮查看推荐课程

### 6. 报告生成

1. **生成报告**
   - 在左侧菜单栏点击"报告生成"
   - 选择报告类型（管理员报告、教师报告、学生报告）
   - 学生报告需要输入学生ID
   - 点击"生成报告"按钮生成报告

## 数据文件格式说明

### students.csv
```csv
student_id,name,age,major
S001,张三,19,计算机科学与技术
S002,李四,20,电子工程
```

### grades.csv
```csv
student_id,course,score,semester,year
S001,高等数学,85,第一学期,2024
S001,大学物理,78,第一学期,2024
```

### attendance.csv
```csv
student_id,date,course,status
S001,2024-03-01,高等数学,present
S001,2024-03-02,大学物理,late
```

### courses.csv
```csv
student_id,course,semester,year
S001,高等数学,第一学期,2024
S001,大学物理,第一学期,2024
```

## 预警机制说明

系统基于以下因素进行风险评估：
- 平均成绩
- 挂科门数
- 出勤率
- 连续挂科次数
- 成绩下降幅度
- 选课数量
- 迟到次数
- 早退次数

风险等级划分：
- **高风险**：存在3个及以上风险因素
- **中风险**：存在2个风险因素
- **低风险**：存在1个风险因素
- **无风险**：无风险因素

## 技术实现

### 数据处理流程
1. 数据加载和清洗
2. 特征工程和数据质量评估
3. 分类模型训练（决策树、逻辑回归）
4. 聚类分析（K-means、DBSCAN）
5. 关联规则挖掘（Apriori）
6. 预警报告生成

### 项目目录结构
- `src/` - 源代码目录
  - `app.py` - Flask后端服务
  - `academic_warning.py` - 学业预警主程序
  - `data_generator.py` - 数据生成器
  - `student_behavior_anomaly_detection.py` - 学生行为异常检测
  - `reset_lock.py` - 重置锁定脚本
  - `data_processing/` - 数据处理模块
  - `classification/` - 分类算法实现
  - `association_rules/` - 关联规则算法
  - `group_analysis/` - 群体特征分析
  - `learning_path_recommendation/` - 学习路径推荐
  - `report_generator/` - 报告生成模块
  - `llm_integration/` - LLM集成模块
  - `student_behavior_representation/` - 学生行为表征
  - `gnn_explanation/` - GNN解释模块
  - `auth/` - 认证模块
- `data/` - 数据文件目录
- `advanced_data/` - 高级数据目录（包含CSV、JSON、Parquet格式）
- `reports/` - 报告和图表文件目录
- `templates/` - 前端模板目录
- `group_visualizations/` - 群体可视化目录
- `docs/` - 文档目录
- `tests/` - 测试文件目录
- `run.py` - 启动脚本
- `requirements.txt` - 依赖包配置

## 注意事项

1. 系统使用的是开发服务器，生产环境请使用专业的WSGI服务器
2. 数据文件必须严格按照模板格式上传，否则可能导致分析失败
3. 预警通知会记录到`reports/warning_notifications.log`文件中
4. 系统会自动生成预警报告`reports/academic_warning_report.csv`和群体分析报告`reports/group_analysis_report.csv`
5. 图表文件（如风险分布图、特征重要性图）会保存到`reports/`目录
6. 群体可视化图表会保存到`group_visualizations/`目录

## 联系方式

如有问题或建议，请联系系统管理员。