import pandas as pd
import numpy as np
import os
import logging
import re
from datetime import datetime

class EASportsFCDataCleaner:
    def __init__(self, input_file='ea_sports_fc_players.xlsx'):
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 设置文件路径
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_file = os.path.join(self.current_dir, input_file)
        
        # 检查输入文件是否存在
        if not os.path.exists(self.input_file):
            self.logger.error(f"输入文件不存在: {self.input_file}")
            raise FileNotFoundError(f"找不到文件: {self.input_file}")
        
        # 读取数据
        self.data = None
        self.load_data()
    
    def load_data(self):
        """加载Excel数据"""
        try:
            self.data = pd.read_excel(self.input_file)
            self.logger.info(f"成功加载数据，共 {len(self.data)} 条记录")
        except Exception as e:
            self.logger.error(f"加载数据失败: {str(e)}")
            raise
    
    def clean_data(self):
        """清洗数据"""
        if self.data is None:
            self.logger.error("没有数据可清洗")
            return
        
        try:
            # 1. 处理缺失值
            self.logger.info("处理缺失值...")
            self.data = self.data.fillna({
                'Name': 'Unknown',
                'OVR': 0,
                'PAC': 0,
                'SHO': 0,
                'PAS': 0,
                'DRI': 0,
                'DEF': 0,
                'PHY': 0
            })
            
            # 2. 确保数值列为整数类型
            numeric_cols = ['OVR', 'PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY']
            for col in numeric_cols:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce').fillna(0).astype(int)
            
            # 3. 清理球员名称（去除特殊字符和多余空格）
            self.data['Name'] = self.data['Name'].apply(lambda x: re.sub(r'[^\w\s]', '', str(x)).strip())
            
            # 4. 添加数据处理时间戳
            self.data['processed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 5. 添加球员位置分类
            self.data['position_category'] = self.data.apply(self.categorize_position, axis=1)
            
            # 6. 添加球员评级分类
            self.data['rating_category'] = self.data['OVR'].apply(self.categorize_rating)
            
            self.logger.info("数据清洗完成")
            return self.data
            
        except Exception as e:
            self.logger.error(f"清洗数据时出错: {str(e)}")
            raise
    
    def categorize_position(self, row):
        """根据能力值分类球员位置"""
        # 简单的位置分类逻辑
        if row['DEF'] > 75 and row['PHY'] > 70:
            return 'Defender'
        elif row['PAC'] > 80 and row['SHO'] > 75:
            return 'Forward'
        elif row['PAS'] > 80 and row['DRI'] > 75:
            return 'Midfielder'
        elif row['DEF'] > 80 and row['PHY'] > 80:
            return 'Center Back'
        else:
            return 'All-rounder'
    
    def categorize_rating(self, ovr):
        """根据总评分类球员等级"""
        if ovr >= 90:
            return 'World Class'
        elif ovr >= 85:
            return 'Elite'
        elif ovr >= 80:
            return 'Star'
        elif ovr >= 75:
            return 'Regular'
        else:
            return 'Prospect'
    
    def save_cleaned_data(self, output_file=None):
        """保存清洗后的数据"""
        if self.data is None:
            self.logger.error("没有数据可保存")
            return
        
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f'ea_sports_fc_players_cleaned_{timestamp}.xlsx'
            
            output_path = os.path.join(self.current_dir, output_file)
            self.data.to_excel(output_path, index=False)
            self.logger.info(f"清洗后的数据已保存到 {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            raise

def main():
    try:
        cleaner = EASportsFCDataCleaner()
        cleaner.clean_data()
        cleaner.save_cleaned_data()
    except Exception as e:
        logging.error(f"数据清洗过程出错: {str(e)}")

if __name__ == "__main__":
    main() 