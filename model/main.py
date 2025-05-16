import pandas as pd
from app.squadRequire import TeamNeedsAnalysis
from app.playersClassify import FootballPlayerAnalysis

def main():
    # 读取球队数据，尝试不同的编码方式
    try:
        team_data = pd.read_csv('SquadInfo.csv', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            team_data = pd.read_csv('SquadInfo.csv', encoding='gbk')
        except UnicodeDecodeError:
            team_data = pd.read_csv('SquadInfo.csv', encoding='gb2312')
    
    # 分析球队需求
    team_analysis = TeamNeedsAnalysis(team_data)
    team_analysis.normalize_data()
    team_needs = team_analysis.analyze_needs()
    
    # 读取球员数据，同样处理编码问题
    try:
        player_analysis = FootballPlayerAnalysis('football_players_cleaned.csv', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            player_analysis = FootballPlayerAnalysis('football_players_cleaned.csv', encoding='gbk')
        except UnicodeDecodeError:
            player_analysis = FootballPlayerAnalysis('football_players_cleaned.csv', encoding='gb2312')
    
    # 分析所有球队的需求
    print("\n各球队需求分析：")
    for _, team in team_needs.iterrows():
        team_name = team['球队']
        recommendations = team_analysis.get_recommended_player_types(team_name)
        
        print(f"\n{team_name}的需求分析：")
        print(f"进攻需求评分: {team['进攻需求']:.2f}")
        print(f"创造力需求评分: {team['创造力需求']:.2f}")
        print(f"防守需求评分: {team['防守需求']:.2f}")
        print(f"主要需求: {team['主要需求']}")
        
        print("\n推荐球员类型：")
        for rec in recommendations:
            print(f"- {rec['类型']} (优先级: {rec['优先级']})")
            print(f"  关键属性: {', '.join(rec['关键属性'])}")
    
    # 获取各位置最佳球员
    positions = ['前锋', '中场', '后卫', '门将']
    print("\n各位置最佳球员：")
    for position in positions:
        top_players = player_analysis.get_top_players(n=3, position=position)
        print(f"\n{position}位置前三名：")
        if '评分' in top_players.columns:
            print(top_players[['球员', '评分']])
        else:
            print(top_players[['球员']])

if __name__ == "__main__":
    main() 