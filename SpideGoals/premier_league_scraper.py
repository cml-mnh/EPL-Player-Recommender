import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from datetime import datetime

class PremierLeagueScraper:
    def __init__(self):
        self.url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        self.headers = self._get_headers()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logging.basicConfig(
            filename=f'scraping_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _get_headers(self):
        """生成随机请求头"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
        ]
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def _random_delay(self):
        """随机延迟，避免请求过快"""
        time.sleep(random.uniform(2, 5))

    def _make_request(self):
        """发送HTTP请求并处理可能的异常"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {str(e)}")
            return None

    def scrape_data(self):
        """抓取数据"""
        self.logger.info("开始抓取数据...")
        response = self._make_request()
        
        if not response:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'stats_squads_shooting_for'})
        
        if not table:
            self.logger.error("未找到目标表格")
            return None

        data = []
        rows = table.find_all('tr')[2:]  # 跳过表头行
        
        for row in rows:
            cols = row.find_all(['th', 'td'])
            if len(cols) > 0:
                team_data = {
                    'Squad': cols[0].text,
                    'Gls': cols[3].text,
                    'Sh': cols[4].text,
                    'G/Sh': cols[9].text
                }
                data.append(team_data)
                self._random_delay()

        return data

    def save_to_excel(self, data):
        """保存数据到Excel"""
        if not data:
            self.logger.error("没有数据可保存")
            return
        
        try:
            df = pd.DataFrame(data)
            filename = f'premier_league_stats_{datetime.now().strftime("%Y%m%d")}.xlsx'
            df.to_excel(filename, index=False)
            self.logger.info(f"数据已保存到 {filename}")
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
