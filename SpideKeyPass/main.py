import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FBrefScraper:
    def __init__(self):
        self.base_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        self.session = requests.Session()
        
    def get_random_headers(self):
        """生成随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def random_delay(self):
        """随机延迟，避免频繁请求"""
        time.sleep(random.uniform(2, 5))

    def fetch_page(self):
        """获取页面内容"""
        try:
            self.random_delay()
            response = self.session.get(
                self.base_url,
                headers=self.get_random_headers(),
                timeout=10
            )
            response.raise_for_status()
            # 添加调试信息
            logging.info(f"页面状态码: {response.status_code}")
            logging.info(f"页面内容长度: {len(response.text)}")
            return response.text
        except requests.RequestException as e:
            logging.error(f"请求失败: {e}")
            return None

    def parse_data(self, html_content):
        """解析页面数据"""
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 找到包含关键传球数据的表格
        table = soup.find('table', {'id': 'stats_squads_passing_for'})
        if not table:
            logging.error("未找到目标表格")
            return None

        # 提取数据
        data = []
        tbody = table.find('tbody')
        if not tbody:
            logging.error("未找到表格主体")
            return None

        rows = tbody.find_all('tr')
        logging.info(f"找到 {len(rows)} 行数据")
        
        for row in rows:
            try:
                # 获取球队名称
                team_element = row.find('th', {'data-stat': 'team'})
                if not team_element:
                    continue
                team_link = team_element.find('a')
                team_name = team_link.text.strip() if team_link else team_element.text.strip()
                
                # 获取KP值（关键传球）
                kp_element = row.find('td', {'data-stat': 'assisted_shots'})
                if not kp_element:
                    continue
                kp_value = kp_element.text.strip()
                
                if team_name and kp_value:
                    row_data = {
                        'Team': team_name,
                        'KP': int(kp_value)  # 转换为整数
                    }
                    data.append(row_data)
                    logging.info(f"成功提取数据: {row_data}")
            
            except Exception as e:
                logging.error(f"处理行时出错: {str(e)}")
                continue

        logging.info(f"总共提取了 {len(data)} 条数据")
        
        # 按KP值降序排序
        data.sort(key=lambda x: x['KP'], reverse=True)
        return data

    def save_to_excel(self, data):
        """保存数据到Excel"""
        if not data:
            logging.error("没有数据可保存")
            return

        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'premier_league_kp_{timestamp}.xlsx'
        
        try:
            # 设置列名
            df.columns = ['球队', '关键传球']
            # 添加排名列
            df.insert(0, '排名', range(1, len(df) + 1))
            df.to_excel(filename, index=False)
            logging.info(f"数据已保存到 {filename}")
        except Exception as e:
            logging.error(f"保存数据失败: {e}")

    def run(self):
        """运行爬虫"""
        logging.info("开始爬取数据...")
        html_content = self.fetch_page()
        if html_content:
            data = self.parse_data(html_content)
            if data:
                self.save_to_excel(data)
            else:
                logging.error("数据解析失败")
        else:
            logging.error("获取页面失败")

if __name__ == "__main__":
    scraper = FBrefScraper()
    scraper.run() 