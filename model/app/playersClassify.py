import pandas as pd
import numpy as np
from pyhive import hive
import os

class PlayersClassify:
    def __init__(self, hive_config):
        """初始化球员分类分析器
        
        Args:
            hive_config (dict): Hive连接配置，包含以下字段：
                - host: Hive服务器地址
                - port: Hive服务器端口
                - username: 用户名
                - password: 密码
                - database: 数据库名
                - table: 表名
        """
        try:
            # 从Hive读取数据
            self.data = self._read_from_hive(hive_config)
            
            # 标准化位置信息
            self.standardize_positions()
            
            # 计算每分钟进球和助攻
            self.calculate_per_minute_stats()
            
            # 计算防守贡献
            self.calculate_defensive_contribution()
            
            print('标准化位置分布:', self.data['标准化位置'].value_counts())
            print('position唯一值:', self.data['position'].unique())
            
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            raise
    
    def _read_from_hive(self, config):
        """从Hive读取数据"""
        try:
            print(f"正在连接到Hive服务器: {config['host']}:{config['port']}")
            print(f"使用数据库: {config['database']}")
            print(f"使用表: {config['table']}")
            
            # 建立Hive连接
            conn = hive.Connection(
                host=config['host'],
                port=config['port'],
                username=config['username'],
                password=config['password'],
                database=config['database'],
                auth='LDAP'  # 或 'CUSTOM'
            )
            
            print("Hive连接成功建立")
            
            # 构建查询语句
            query = f"""
            SELECT 
                player_name,
                club_name,
                age,
                position,
                matches_played,
                minutes_played,
                goals,
                assists,
                yellow_cards,
                red_cards,
                pass_success_rate,
                chances_created,
                headers_won,
                rating,
                market_value
            FROM {config['table']}
            """
            
            print(f"执行查询: {query}")
            
            # 执行查询并转换为DataFrame
            df = pd.read_sql(query, conn)
            
            print(f"成功获取数据，共 {len(df)} 条记录")
            
            # 关闭连接
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"从Hive读取数据失败: {str(e)}")
            print(f"连接配置: {config}")
            raise
    
    def standardize_positions(self):
        """标准化球员位置信息"""
        position_mapping = {
            '中锋': '前锋',
            '二前锋': '前锋',
            '左边锋': '前锋',
            '右边锋': '前锋',
            '中场': '中场',
            '后腰': '中场',
            '前腰': '中场',
            '左前卫': '中场',
            '右前卫': '中场',
            '后卫': '后卫',
            '左后卫': '后卫',
            '右后卫': '后卫',
            '中后卫': '后卫',
            '门将': '门将'
        }
        
        self.data['标准化位置'] = self.data['position'].map(position_mapping)
    
    def calculate_per_minute_stats(self):
        """计算每分钟进球和助攻"""
        self.data['minutes_played'] = pd.to_numeric(self.data['minutes_played'], errors='coerce')
        self.data['goals'] = pd.to_numeric(self.data['goals'], errors='coerce')
        self.data['assists'] = pd.to_numeric(self.data['assists'], errors='coerce')
        self.data['rating'] = pd.to_numeric(self.data['rating'], errors='coerce')
        self.data['pass_success_rate'] = pd.to_numeric(self.data['pass_success_rate'], errors='coerce')
        self.data['每分钟进球'] = self.data['goals'] / self.data['minutes_played']
        self.data['每分钟助攻'] = self.data['assists'] / self.data['minutes_played']
        self.data['每分钟进球'] = self.data['每分钟进球'].replace([np.inf, -np.inf], 0).fillna(0)
        self.data['每分钟助攻'] = self.data['每分钟助攻'].replace([np.inf, -np.inf], 0).fillna(0)
    
    def calculate_defensive_contribution(self):
        """计算防守贡献分数"""
        # 标准化防守相关数据
        defensive_columns = ['yellow_cards', 'red_cards']
        for col in defensive_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
                self.data[col] = self.data[col].fillna(0)
        
        # 计算防守贡献分数
        self.data['防守贡献'] = (
            self.data['yellow_cards'].fillna(0) * 0.5 +
            self.data['red_cards'].fillna(0) * 1.0
        )
    
    def analyze_by_position(self, position):
        """分析特定位置的球员数据"""
        self.data['rating'] = pd.to_numeric(self.data['rating'], errors='coerce')
        self.data['pass_success_rate'] = pd.to_numeric(self.data['pass_success_rate'], errors='coerce')
        if position not in self.data['标准化位置'].unique():
            return pd.DataFrame()
        position_data = self.data[self.data['标准化位置'] == position]
        stats = {
            '平均评分': position_data['rating'].mean(),
            '平均进球': position_data['goals'].mean(),
            '平均助攻': position_data['assists'].mean(),
            '平均上场时间': position_data['minutes_played'].mean(),
            '平均传球成功率': position_data['pass_success_rate'].mean() if 'pass_success_rate' in position_data.columns else 0
        }
        return pd.DataFrame([stats]) 