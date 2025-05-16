# 球员推荐系统

这是一个基于 Flask 的球员推荐系统，可以根据用户的需求推荐合适的球员。支持从 Hive 数据库或 CSV 文件读取数据。

## 功能特点

- 支持按位置筛选球员
- 支持自然语言描述球员需求
- 智能分析球员数据并计算匹配度
- 展示详细的球员技术数据和分析结果
- 支持从 Hive 数据库或 CSV 文件读取数据

## 安装说明

1. 确保已安装 Python 3.7 或更高版本
2. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 从 CSV 文件读取数据

1. 将球员数据文件 `football_players_cleaned.csv` 放在项目根目录下
2. 运行服务器：
   ```bash
   python app.py
   ```

### 从 Hive 数据库读取数据

1. 设置环境变量（或直接在代码中配置）：
   ```bash
   # Windows
   set HIVE_HOST=your_hive_host
   set HIVE_PORT=10000
   set HIVE_USERNAME=your_username
   set HIVE_PASSWORD=your_password
   set HIVE_DATABASE=your_database
   set HIVE_TABLE=your_table

   # Linux/Mac
   export HIVE_HOST=your_hive_host
   export HIVE_PORT=10000
   export HIVE_USERNAME=your_username
   export HIVE_PASSWORD=your_password
   export HIVE_DATABASE=your_database
   export HIVE_TABLE=your_table
   ```

2. 运行服务器：
   ```bash
   python app.py
   ```

3. 在浏览器中访问 `http://localhost:5000`

## 数据格式要求

### CSV 文件格式

CSV 文件应包含以下字段：
- 球员：球员姓名
- 位置：球员位置（如 ST、CF、LW 等）
- 进球：进球数
- 助攻：助攻数
- 上场时间：上场时间（分钟）
- 评分：球员评分
- 抢断：抢断次数
- 拦截：拦截次数
- 解围：解围次数
- 封堵：封堵次数

### Hive 表格式

Hive 表应包含与 CSV 文件相同的字段结构。

## 注意事项

- 确保 CSV 文件使用正确的编码格式（支持 UTF-8、GBK、GB2312、UTF-16）
- 数据中的数值字段应为数字类型
- 如果某些字段缺失，系统会自动处理并填充默认值
- 如果 Hive 连接失败，系统会自动尝试从 CSV 文件读取数据 