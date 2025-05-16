import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

class PremierLeagueScraper:
    def __init__(self):
        self.url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_selenium()

    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_team_stats(self):
        try:
            time.sleep(random.uniform(1, 3))
            
            self.driver.get(self.url)
            
            # 等待表格加载 - 注意这里改为正确的表格ID
            wait = WebDriverWait(self.driver, 10)
            table = wait.until(EC.presence_of_element_located((By.ID, "stats_squads_keeper_for")))
            
            # 解析页面
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            stats_table = soup.find('table', {'id': 'stats_squads_keeper_for'})
            
            data = []
            # 跳过表头行
            for row in stats_table.find_all('tr')[1:]:
                cols = row.find_all(['td', 'th'])
                if cols:
                    team_data = {
                        'Squad': cols[0].text.strip(),  # 球队名在第一列
                        'GA': cols[6].text.strip(),     # GA (Goals Against) 在第7列
                        'MP': cols[2].text.strip(),     # 比赛场次
                        'Save%': cols[10].text.strip(), # 扑救成功率
                        'CS': cols[14].text.strip(),    # 零封场次
                        'CS%': cols[15].text.strip()    # 零封率
                    }
                    data.append(team_data)
            
            return data
            
        except Exception as e:
            raise Exception(f"数据抓取失败: {str(e)}")
        
        finally:
            self.driver.quit() 