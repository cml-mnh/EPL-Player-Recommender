from flask import Flask, request, jsonify, render_template
from squadRequire import SquadRequire
from app.playersClassify import PlayersClassify
import pandas as pd
import os

app = Flask(__name__)

# Hive配置
HIVE_CONFIG = {
    'host': os.getenv('HIVE_HOST', 'localhost'),
    'port': int(os.getenv('HIVE_PORT', 10000)),
    'username': os.getenv('HIVE_USERNAME', ''),
    'password': os.getenv('HIVE_PASSWORD', ''),
    'database': os.getenv('HIVE_DATABASE', 'default'),
    'table': os.getenv('HIVE_TABLE', 'football_players')
}

# 初始化推荐系统
try:
    # 尝试从Hive读取数据
    players_classify = PlayersClassify(hive_config=HIVE_CONFIG)
except Exception as e:
    print(f"从Hive读取数据失败，尝试从CSV文件读取: {str(e)}")
    players_classify = PlayersClassify()

squad_require = SquadRequire()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # 获取表单数据
        position = request.form.get('position', '')
        requirements = request.form.get('requirements', '')
        
        # 获取推荐结果
        recommendations = squad_require.get_recommendations(position, requirements)
        
        # 获取关键词
        keywords = squad_require.extract_keywords(requirements)
        
        return jsonify({
            'recommendations': recommendations,
            'keywords': keywords
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 