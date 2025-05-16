from flask import Flask, request, jsonify, render_template
from squadRequire import SquadRequire
from playersClassify import PlayersClassify
import pandas as pd
import traceback

app = Flask(__name__)

# Hive配置
hive_config = {
    'host': 'node1',        # Hive服务器地址
    'port': 10000,          # Hive服务器端口
    'username': 'root',     # 用户名
    'password': 'xc20040203',
    'database': 'sc',       # 数据库名
    'table': 'football_players'  # 表名
}

# 初始化推荐系统
squad_require = SquadRequire(hive_config=hive_config)
players_classify = PlayersClassify(hive_config=hive_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        position = request.form.get('position', '')
        requirements = request.form.get('requirements', '')
        print('position:', position, 'requirements:', requirements)
        recommendations = squad_require.get_recommendations(position, requirements)
        keywords = squad_require.extract_keywords(requirements)
        return jsonify({
            'recommendations': recommendations,
            'keywords': keywords
        })
    except Exception as e:
        print(traceback.format_exc())  # 打印完整错误堆栈
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 