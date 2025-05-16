import pandas as pd
import numpy as np

class TeamNeedsAnalysis:
    def __init__(self, team_data):
        self.data = team_data
        self.normalized_data = None
        self.team_needs = None
        
        # 定义可能的列名映射
        self.column_mapping = {
            'team_name': ['球队', 'Team', 'team', '编码名称', '球队名称'],
            'goals': ['进球', 'Goals', 'goals', '进球数'],
            'shots': ['射门', 'Shots', 'shots', '射门次数'],
            'conversion_rate': ['进球转化率', 'Conversion Rate', 'conversion_rate', '转化率'],
            'key_passes': ['关键传球', 'Key Passes', 'key_passes', '关键传球次数'],
            'goals_conceded': ['失球', 'Goals Conceded', 'goals_conceded', '失球数']
        }
        
        # 标准化列名
        self._standardize_columns()
        
        # 检查必要的列是否存在
        self._check_required_columns()
    
    def _standardize_columns(self):
        """标准化列名"""
        for standard_name, possible_names in self.column_mapping.items():
            for name in possible_names:
                if name in self.data.columns:
                    self.data = self.data.rename(columns={name: standard_name})
                    break
    
    def _check_required_columns(self):
        """检查必要的列是否存在"""
        required_columns = ['team_name', 'goals', 'shots', 'conversion_rate', 'key_passes', 'goals_conceded']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            raise ValueError(f"缺少必要的列: {', '.join(missing_columns)}")
    
    def normalize_data(self):
        """标准化数据，便于比较"""
        if self.normalized_data is not None:
            return
            
        normalized = self.data.copy()
        for col in normalized.columns:
            if col == 'team_name':
                continue
            if col == 'conversion_rate':  # 特殊处理百分比数据
                normalized[col] = normalized[col] * 100  # 转换为百分比值
            normalized[col] = (normalized[col] - normalized[col].min()) / \
                            (normalized[col].max() - normalized[col].min())
        self.normalized_data = normalized
    
    def analyze_needs(self):
        """分析各队需求"""
        if self.normalized_data is None:
            self.normalize_data()
            
        needs = []
        for _, row in self.normalized_data.iterrows():
            team = row['team_name']
            
            # 进攻效率分析 (进球数、射门次数、进球转化率)
            offensive_score = 0.4*row['goals'] + 0.3*(1-row['shots']) + 0.3*row['conversion_rate']
            
            # 创造机会分析 (关键传球次数)
            creativity_score = row['key_passes']
            
            # 防守分析 (失球数)
            defensive_score = 1 - row['goals_conceded']
            
            # 确定需求优先级
            needs.append({
                '球队': team,
                '进攻需求': 1 - offensive_score,
                '创造力需求': 1 - creativity_score,
                '防守需求': 1 - defensive_score,
                '主要需求': self._determine_primary_need(offensive_score, creativity_score, defensive_score)
            })
            
        self.team_needs = pd.DataFrame(needs)
        return self.team_needs
    
    def _determine_primary_need(self, offensive, creativity, defensive):
        """确定最主要需求"""
        needs = {
            '进攻球员': 1 - offensive,
            '创造力中场': 1 - creativity,
            '防守球员': 1 - defensive
        }
        return max(needs, key=needs.get)
    
    def get_recommended_player_types(self, team_name):
        """获取推荐球员类型"""
        if self.team_needs is None:
            self.analyze_needs()
            
        team_need = self.team_needs[self.team_needs['球队'] == team_name].iloc[0]
        
        recommendations = []
        
        # 进攻球员推荐
        if team_need['进攻需求'] > 0.6:
            recommendations.append({
                '类型': '高效射手',
                '关键属性': ['高进球转化率', '射门精度', '无球跑动'],
                '优先级': '高'
            })
        elif team_need['进攻需求'] > 0.4:
            recommendations.append({
                '类型': '全能前锋',
                '关键属性': ['射门能力', '身体素质', '头球能力'],
                '优先级': '中'
            })
            
        # 创造力中场推荐
        if team_need['创造力需求'] > 0.6:
            recommendations.append({
                '类型': '组织核心',
                '关键属性': ['视野', '传球', '关键传球能力'],
                '优先级': '高'
            })
        elif team_need['创造力需求'] > 0.4:
            recommendations.append({
                '类型': '进攻型中场',
                '关键属性': ['盘带', '远射', '短传'],
                '优先级': '中'
            })
            
        # 防守球员推荐
        if team_need['防守需求'] > 0.6:
            recommendations.append({
                '类型': '防守型中场',
                '关键属性': ['抢断', '拦截', '位置感'],
                '优先级': '高'
            })
        elif team_need['防守需求'] > 0.4:
            recommendations.append({
                '类型': '中后卫',
                '关键属性': ['头球', '盯人', '解围'],
                '优先级': '中'
            })
            
        # 按优先级排序
        recommendations.sort(key=lambda x: x['优先级'], reverse=True)
        return recommendations