import pandas as pd
import os
import logging

class PlayerClassifier:
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('classifier.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 创建输出目录
        self.output_dir = 'classified_players'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def classify_players(self, input_file='football_players.csv'):
        try:
            # 读取CSV文件
            self.logger.info(f"正在读取文件: {input_file}")
            df = pd.read_csv(input_file, encoding='utf-8-sig')
            
            # 获取所有不同的位置
            positions = df['位置'].unique()
            self.logger.info(f"找到以下位置: {', '.join(positions)}")
            
            # 按位置分类并保存
            for position in positions:
                if pd.isna(position):  # 处理空值
                    position_name = '未知'
                    position_df = df[df['位置'].isna()]
                else:
                    position_name = position
                    position_df = df[df['位置'] == position]
                
                # 按评分降序排序
                position_df = position_df.sort_values(by='评分', ascending=False)
                
                # 生成输出文件名
                output_file = os.path.join(self.output_dir, f'{position_name}_players.csv')
                
                # 保存文件
                position_df.to_csv(output_file, index=False, encoding='utf-8-sig')
                
                self.logger.info(f"已保存{position_name}位置球员数据，共 {len(position_df)} 条记录")
                
                # 打印该位置的前5名球员
                print(f"\n{position_name}位置前5名球员:")
                top_5 = position_df[['球员', '俱乐部', '评分']].head()
                print(top_5.to_string(index=False))
                print("-" * 50)
            
            # 创建一个汇总报告
            self.create_summary_report(df, positions)
            
        except Exception as e:
            self.logger.error(f"分类过程出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def create_summary_report(self, df, positions):
        """创建汇总报告"""
        try:
            summary_data = []
            
            for position in positions:
                if pd.isna(position):
                    position_name = '未知'
                    position_df = df[df['位置'].isna()]
                else:
                    position_name = position
                    position_df = df[df['位置'] == position]
                
                summary_data.append({
                    '位置': position_name,
                    '球员数量': len(position_df),
                    '平均评分': position_df['评分'].mean(),
                    '最高评分': position_df['评分'].max(),
                    '最低评分': position_df['评分'].min(),
                    '平均进球': position_df['进球'].astype(float).mean(),
                    '平均助攻': position_df['助攻'].astype(float).mean()
                })
            
            # 创建汇总报告
            summary_df = pd.DataFrame(summary_data)
            summary_file = os.path.join(self.output_dir, 'position_summary.csv')
            summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
            
            self.logger.info("已生成位置汇总报告")
            print("\n位置汇总报告:")
            print(summary_df.to_string(index=False))
            
        except Exception as e:
            self.logger.error(f"创建汇总报告时出错: {str(e)}")

def main():
    classifier = PlayerClassifier()
    classifier.classify_players()

if __name__ == "__main__":
    main()
