import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import logging
import os

class EASportsFCScraper:
    def __init__(self):
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 使用静态 User Agent
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        
        # 初始化 Selenium
        self.setup_driver()
        
    def setup_driver(self):
        """配置 Selenium WebDriver"""
        try:
            options = webdriver.ChromeOptions()
            
            # 添加基本配置
            options.add_argument('--start-maximized')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # 添加用户代理
            options.add_argument(f'user-agent={self.ua}')
            
            # 禁用自动化标记
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 初始化驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            self.logger.error(f"设置驱动时出错: {str(e)}")
            raise

    def get_player_stats(self):
        """获取球员数据"""
        url = "https://www.ea.com/zh-hant/games/ea-sports-fc/ratings?gender=0&team=1"
        max_retries = 3
        player_data = {
            'Name': [], 'OVR': [], 'PAC': [], 'SHO': [], 
            'PAS': [], 'DRI': [], 'DEF': [], 'PHY': []
        }
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"正在尝试获取数据，第 {attempt + 1} 次...")
                
                # 访问页面
                self.driver.get(url)
                time.sleep(random.uniform(5, 8))
                
                # 处理可能的cookie提示
                try:
                    cookie_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Accept') or contains(text(), '接受')]")
                    if cookie_buttons:
                        cookie_buttons[0].click()
                        time.sleep(2)
                except:
                    pass
                
                # 等待表格加载
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "Table_row__eoyUr"))
                )
                
                # 获取所有球员行
                rows = self.driver.find_elements(By.CLASS_NAME, "Table_row__eoyUr")
                
                for row in rows:
                    try:
                        # 获取球员名称
                        name = row.find_element(By.CSS_SELECTOR, "div.Table_profileContent__0t2_u").text.split('\n')[-1]
                        
                        # 获取能力值
                        stats = row.find_elements(By.CSS_SELECTOR, "span.Table_statCellValue__zn5Cx")
                        if len(stats) >= 7:  # 确保有足够的数据
                            player_data['Name'].append(name)
                            player_data['OVR'].append(stats[0].text.split('\n')[0])
                            player_data['PAC'].append(stats[1].text.split('\n')[0])
                            player_data['SHO'].append(stats[2].text.split('\n')[0])
                            player_data['PAS'].append(stats[3].text.split('\n')[0])
                            player_data['DRI'].append(stats[4].text.split('\n')[0])
                            player_data['DEF'].append(stats[5].text.split('\n')[0])
                            player_data['PHY'].append(stats[6].text.split('\n')[0])
                            
                    except Exception as e:
                        self.logger.error(f"处理球员数据时出错: {str(e)}")
                        continue
                
                if len(player_data['Name']) > 0:
                    self.logger.info(f"成功获取 {len(player_data['Name'])} 名球员的数据")
                    return player_data
                
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                self.logger.error(f"获取数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(10, 15))
                else:
                    raise Exception("无法获取数据")
    
    def save_to_excel(self, data, filename='ea_sports_fc_players.xlsx'):
        """保存数据到Excel文件"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, filename)
            
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filepath = os.path.join(current_dir, f'ea_sports_fc_players_{timestamp}.xlsx')
            
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            self.logger.info(f"数据已保存到 {filepath}")
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            raise
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

def main():
    scraper = EASportsFCScraper()
    
    try:
        data = scraper.get_player_stats()
        scraper.save_to_excel(data)
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 