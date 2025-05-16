import pandas as pd
from datetime import datetime

class DataProcessor:
    def process_data(self, raw_data):
        # 转换为DataFrame
        df = pd.DataFrame(raw_data)
        
        # 数据清洗和转换
        df['GA'] = pd.to_numeric(df['GA'], errors='coerce')
        df['MP'] = pd.to_numeric(df['MP'], errors='coerce')
        df['Save%'] = pd.to_numeric(df['Save%'], errors='coerce')
        df['CS'] = pd.to_numeric(df['CS'], errors='coerce')
        df['CS%'] = pd.to_numeric(df['CS%'], errors='coerce')
        
        # 按照失球数排序
        df = df.sort_values('GA', ascending=True)
        
        return df
    
    def save_to_excel(self, df, filename):
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename.split('.')[0]}_{timestamp}.xlsx"
        
        # 设置Excel写入选项
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        # 保存到Excel，添加列宽设置
        df.to_excel(writer, index=False, sheet_name='英超球队失球数据')
        
        # 获取worksheet
        worksheet = writer.sheets['英超球队失球数据']
        
        # 设置列宽
        worksheet.column_dimensions['A'].width = 20  # Squad列
        worksheet.column_dimensions['B'].width = 10  # GA列
        worksheet.column_dimensions['C'].width = 10  # MP列
        worksheet.column_dimensions['D'].width = 10  # Save%列
        worksheet.column_dimensions['E'].width = 10  # CS列
        worksheet.column_dimensions['F'].width = 10  # CS%列
        
        # 保存文件
        writer.close() 