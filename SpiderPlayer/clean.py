import pandas as pd
import numpy as np

def clean_football_players(input_file='football_players.csv', output_file='football_players_cleaned.csv'):
    # 读取数据
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    # 去除全空行
    df.dropna(how='all', inplace=True)
    
    # 去除重复行
    df.drop_duplicates(inplace=True)
    
    # 去除各列首尾空格
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 处理数值列
    for col in ['评分', '进球', '助攻']:
        if col in df.columns:
            # 非数字转为NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # 缺失值填充为0
            df[col] = df[col].fillna(0)
    
    # 统一"位置"字段
    if '位置' in df.columns:
        # 去除空格、统一大小写
        df['位置'] = df['位置'].astype(str).str.strip().str.upper()
        # 常见别名合并（可根据实际情况扩展）
        position_map = {
            'GK': '门将', 'GOALKEEPER': '门将',
            'DF': '后卫', 'DEFENDER': '后卫',
            'MF': '中场', 'MIDFIELDER': '中场',
            'FW': '前锋', 'FORWARD': '前锋'
        }
        df['位置'] = df['位置'].replace(position_map)
        # 还原为中文
        df['位置'] = df['位置'].replace({
            '门将': '门将',
            '后卫': '后卫',
            '中场': '中场',
            '前锋': '前锋'
        })
        # 空值或未知统一
        df['位置'] = df['位置'].replace({'NAN': '未知', 'NONE': '未知', '': '未知'})
    
    # 保存清洗后的数据
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"清洗完成，已保存为 {output_file}")

if __name__ == '__main__':
    clean_football_players()
