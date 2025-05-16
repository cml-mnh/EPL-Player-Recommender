import time
import random
from scraper import PremierLeagueScraper
from data_processor import DataProcessor
from utils import setup_logging
from typing import Optional
import sys

def main(max_retries: int = 3, retry_delay: int = 5) -> None:
    # 设置日志
    logger = setup_logging()
    
    for attempt in range(max_retries):
        try:
            # 初始化爬虫
            logger.info("正在初始化爬虫...")
            scraper = PremierLeagueScraper()
            
            # 获取数据
            logger.info("开始获取球队数据...")
            raw_data = scraper.get_team_stats()
            
            if not raw_data:
                raise ValueError("未能获取到有效数据")
                
            # 处理数据
            logger.info("正在处理数据...")
            processor = DataProcessor()
            processed_data = processor.process_data(raw_data)
            
            # 保存到Excel
            output_file = 'premier_league_stats.xlsx'
            logger.info(f"正在将数据保存到 {output_file}...")
            processor.save_to_excel(processed_data, output_file)
            
            logger.info("数据抓取完成并保存到Excel文件")
            break  # 成功完成，退出重试循环
            
        except Exception as e:
            logger.error(f"第 {attempt + 1} 次尝试失败: {str(e)}")
            if attempt < max_retries - 1:
                sleep_time = retry_delay * (attempt + 1)  # 递增延迟
                logger.info(f"等待 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)
            else:
                logger.error("达到最大重试次数，程序退出")
                sys.exit(1)

if __name__ == "__main__":
    main() 