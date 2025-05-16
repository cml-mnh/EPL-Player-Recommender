import pandas as pd
import numpy as np

class PlayersClassify:
    def __init__(self, file_path='football_players_cleaned.csv'):
        """初始化球员分类分析器"""
        try:
            # 尝试不同的编码方式读取CSV文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            for encoding in encodings:
                try:
                    self.data = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error reading file with {encoding} encoding: {str(e)}")
                    continue
            else:
                raise Exception("无法读取CSV文件，请检查文件编码")
            
            # 标准化位置信息
            self.standardize_positions()
            
            # 计算每分钟进球和助攻
            self.calculate_per_minute_stats()
            
            # 计算防守贡献
            self.calculate_defensive_contribution()
            
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            raise
    
    def standardize_positions(self):
        """标准化球员位置信息"""
        position_mapping = {
            'ST': '前锋',
            'CF': '前锋',
            'LW': '前锋',
            'RW': '前锋',
            'CAM': '中场',
            'CM': '中场',
            'CDM': '中场',
            'LM': '中场',
            'RM': '中场',
            'CB': '后卫',
            'LB': '后卫',
            'RB': '后卫',
            'LWB': '后卫',
            'RWB': '后卫',
            'GK': '门将'
        }
        
        self.data['标准化位置'] = self.data['位置'].map(position_mapping)
    
    def calculate_per_minute_stats(self):
        """计算每分钟进球和助攻"""
        # 将上场时间转换为分钟
        self.data['上场时间'] = pd.to_numeric(self.data['上场时间'], errors='coerce')
        
        # 计算每分钟进球和助攻
        self.data['每分钟进球'] = self.data['进球'] / self.data['上场时间']
        self.data['每分钟助攻'] = self.data['助攻'] / self.data['上场时间']
        
        # 处理无穷大和NaN值
        self.data['每分钟进球'] = self.data['每分钟进球'].replace([np.inf, -np.inf], 0)
        self.data['每分钟助攻'] = self.data['每分钟助攻'].replace([np.inf, -np.inf], 0)
        self.data['每分钟进球'] = self.data['每分钟进球'].fillna(0)
        self.data['每分钟助攻'] = self.data['每分钟助攻'].fillna(0)
    
    def calculate_defensive_contribution(self):
        """计算防守贡献分数"""
        # 标准化防守相关数据
        defensive_columns = ['抢断', '拦截', '解围', '封堵']
        for col in defensive_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
                self.data[col] = self.data[col].fillna(0)
        
        # 计算防守贡献分数
        self.data['防守贡献'] = (
            self.data['抢断'].fillna(0) * 1.0 +
            self.data['拦截'].fillna(0) * 1.0 +
            self.data['解围'].fillna(0) * 0.5 +
            self.data['封堵'].fillna(0) * 0.5
        )
    
    def analyze_by_position(self, position):
        """分析特定位置的球员数据"""
        if position not in self.data['标准化位置'].unique():
            return pd.DataFrame()
        
        position_data = self.data[self.data['标准化位置'] == position]
        
        # 计算位置相关的统计数据
        stats = {
            '平均评分': position_data['评分'].mean(),
            '平均进球': position_data['进球'].mean(),
            '平均助攻': position_data['助攻'].mean(),
            '平均上场时间': position_data['上场时间'].mean(),
            '平均防守贡献': position_data['防守贡献'].mean() if '防守贡献' in position_data.columns else 0
        }
        
        return pd.DataFrame([stats])