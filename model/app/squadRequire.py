import pandas as pd
import numpy as np
import jieba
import jieba.analyse
from playersClassify import PlayersClassify

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

class SquadRequire:
    def __init__(self, hive_config):
        """初始化球队需求分析器
        
        Args:
            hive_config (dict): Hive连接配置
        """
        self.players_classify = PlayersClassify(hive_config)
        
        # 关键词映射字典
        self.KEYWORD_MAPPING = {
            '进攻': ['goals', '进球', '射门', '得分', '前锋'],
            '创造力': ['assists', '传球', '助攻', '组织', '视野', '中场', 'chances_created'],
            '防守': ['yellow_cards', 'red_cards', 'headers_won', '后卫', '门将'],
            '效率': ['pass_success_rate', '效率', '转化率', '成功率'],
            '技术': ['rating', '技术', '控球', '盘带', '过人'],
            '体能': ['minutes_played', '体能', '速度', '耐力', '力量']
        }
    
    def extract_keywords(self, text):
        """提取用户输入的关键词"""
        if not text:
            return []
            
        # 使用jieba提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=5)
        
        # 将关键词映射到标准类别
        mapped_keywords = set()
        for keyword in keywords:
            for category, words in self.KEYWORD_MAPPING.items():
                if any(word in keyword for word in words):
                    mapped_keywords.add(category)
        
        return list(mapped_keywords)
    
    def calculate_player_score(self, player, keywords, position):
        """计算球员匹配度分数"""
        score = 0
        
        # 位置匹配度
        if position and player['标准化位置'] == position:
            score += 30
        
        # 关键词匹配度
        for keyword in keywords:
            if keyword == '进攻' and '每分钟进球' in player:
                score += float(player['每分钟进球'] or 0) * 20
            elif keyword == '创造力' and '每分钟助攻' in player:
                score += float(player['每分钟助攻'] or 0) * 20
            elif keyword == '防守' and 'yellow_cards' in player and 'red_cards' in player:
                score += (float(player['yellow_cards'] or 0) * 0.5 + float(player['red_cards'] or 0) * 1.0) * 10
            elif keyword == '效率' and 'pass_success_rate' in player:
                score += float(player['pass_success_rate'] or 0) * 15
            elif keyword == '技术' and 'rating' in player:
                score += float(player['rating'] or 0) * 10
            elif keyword == '体能' and 'minutes_played' in player:
                score += float(player['minutes_played'] or 0) * 0.01
        
        return score
    
    def get_recommendations(self, position, requirements):
        """获取球员推荐列表"""
        keywords = self.extract_keywords(requirements)
        print('提取关键词:', keywords)
        players = self.players_classify.data.to_dict('records')
        players = [p for p in players if not position or p['标准化位置'] == position]
        player_scores = []
        for player in players:
            score = self.calculate_player_score(player, keywords, position)
            if score > 0:
                player_scores.append({
                    'player': player,
                    'score': score
                })
        print(f'匹配到的球员数量: {len(player_scores)}')
        if player_scores:
            print('前3名分数:', [x['score'] for x in player_scores[:3]])
        
        # 按分数排序
        player_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 获取前5名球员的详细分析
        recommendations = []
        for item in player_scores[:5]:
            player = item['player']
            position_analysis = self.players_classify.analyze_by_position(player['标准化位置'])
            if isinstance(position_analysis, pd.DataFrame) and not position_analysis.empty:
                position_analysis_dict = position_analysis.iloc[0].to_dict()
            else:
                position_analysis_dict = {}

            # 英文key到中文的映射
            key_map = {
                'goals': '进球',
                'assists': '助攻',
                'minutes_played': '上场时间',
                'rating': '评分',
                'pass_success_rate': '传球成功率'
            }

            def cmp(key, default='N/A'):
                zh_key = key_map.get(key, key)
                return {
                    'value': player.get(key, default),
                    'avg': position_analysis_dict.get(f'平均{zh_key}', default)
                }

            recommendations.append({
                '基本信息': {
                    '姓名': player['player_name'],
                    '俱乐部': player['club_name'],
                    '位置': player['标准化位置'],
                    '匹配度': f"{item['score']:.1f}%"
                },
                '技术数据': {
                    '进球': cmp('goals'),
                    '助攻': cmp('assists'),
                    '上场时间': cmp('minutes_played'),
                    '评分': cmp('rating'),
                    '传球成功率': cmp('pass_success_rate')
                }
            })
        
        return recommendations