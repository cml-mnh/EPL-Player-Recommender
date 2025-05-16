import requests

from bs4 import BeautifulSoup

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

import time

import pandas as pd

import random

import urllib3

import ssl



class PlayerScraper:

    def __init__(self):

        # 设置请求头

        self.headers = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',

            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',

            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',

            'Connection': 'keep-alive'

        }

        

        # 初始化selenium

        options = webdriver.ChromeOptions()

        options.add_argument('--headless')  # 无头模式

        options.add_argument('--disable-gpu')

        options.add_argument('--no-sandbox')

        options.add_argument('--disable-dev-shm-usage')

        options.add_argument('--ignore-certificate-errors')

        options.add_argument('--ignore-ssl-errors')

        # 添加新的参数来解决WebGL问题

        options.add_argument('--disable-software-rasterizer')

        options.add_argument('--disable-webgl')

        options.add_argument('--disable-webgl2')

        

        # 设置窗口大小，避免响应式布局问题

        options.add_argument('--window-size=1920,1080')

        

        # 使用webdriver_manager自动管理ChromeDriver

        service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=options)

        

        # 设置页面加载超时时间

        self.driver.set_page_load_timeout(30)

        self.driver.set_script_timeout(30)

        

    def get_players_urls(self, team_url):

        """获取球队所有球员的链接"""

        max_retries = 3

        retry_count = 0

        

        while retry_count < max_retries:

            try:

                self.driver.get(team_url)

                time.sleep(random.uniform(3, 5))  # 增加等待时间

                

                # 等待球员表格加载

                WebDriverWait(self.driver, 20).until(

                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))

                )

                

                # 获取所有球员行

                players = []

                rows = self.driver.find_elements(By.CSS_SELECTOR, "tr[role='row']")

                

                for row in rows:

                    try:

                        link_element = row.find_element(By.CSS_SELECTOR, "td.text-left a")

                        name_element = row.find_element(By.CSS_SELECTOR, "td.text-left a div.limittext")

                        

                        player_link = link_element.get_attribute('href')

                        player_name = name_element.text.split('\u00a0')[0]  # 去除黄牌等标记

                        

                        if player_link and player_name:

                            players.append((player_link, player_name))

                    except:

                        continue

                

                if players:

                    return players

                

                print("未找到球员列表，重试...")

                retry_count += 1

                time.sleep(3)

            

            except Exception as e:

                print(f"获取球员列表失败 {retry_count + 1}/{max_retries}: {str(e)}")

                retry_count += 1

                time.sleep(5)

        

        raise Exception("获取球员列表失败")

    

    def get_player_history(self, player_url, player_name):

        """获取球员历史身价数据"""

        max_retries = 3

        retry_count = 0

        

        while retry_count < max_retries:

            try:

                self.driver.get(player_url)

                time.sleep(random.uniform(3, 5))  # 增加等待时间

                

                # 等待页面加载完成

                WebDriverWait(self.driver, 20).until(

                    EC.presence_of_element_located((By.CSS_SELECTOR, ".highcharts-container"))

                )

                

                # 等待确保图表完全加载

                time.sleep(2)

                

                # 获取身价图表数据

                chart_data = self.driver.execute_script("""

                    try {

                        // 等待Highcharts加载

                        if (typeof Highcharts === 'undefined') return null;

                        

                        // 查找身价图表

                        var valueChart = null;

                        var charts = document.querySelectorAll('.highcharts-container');

                        

                        for (var i = 0; i < charts.length; i++) {

                            var paths = charts[i].querySelectorAll('path[fill^="rgba(39,174,96"]');

                            if (paths.length > 0) {

                                valueChart = Highcharts.charts[i];

                                break;

                            }

                        }

                        

                        if (!valueChart) return null;

                        

                        // 获取数据

                        var data = [];

                        var series = valueChart.series[0];

                        var categories = valueChart.xAxis[0].categories;

                        

                        for (var i = 0; i < series.points.length; i++) {

                            var point = series.points[i];

                            data.push({

                                date: categories[i],

                                value: point.y

                            });

                        }

                        

                        return data;

                    } catch (e) {

                        console.error(e);

                        return null;

                    }

                """)

                

                if not chart_data:

                    print(f"未找到 {player_name} 的身价数据")

                    retry_count += 1

                    continue

                

                # 整理数据

                data = {

                    'player_name': [],

                    'date': [],

                    'value': [],

                    'club': [],

                    'age': []

                }

                

                for point in chart_data:

                    data['player_name'].append(player_name)

                    data['date'].append(point['date'])

                    value = point['value']

                    if value is not None:

                        value = float(value) / 10000  # 转换为万

                    data['value'].append(value)

                    data['club'].append('')  # 暂不获取俱乐部信息

                    data['age'].append('')   # 暂不获取年龄信息

                

                print(f"成功获取 {player_name} 的身价数据")

                return data

                

            except Exception as e:

                print(f"获取 {player_name} 身价数据失败 {retry_count + 1}/{max_retries}: {str(e)}")

                retry_count += 1

                time.sleep(5)

        

        return None

    

    def save_to_csv(self, data, filename='player_values.csv'):

        """保存数据到CSV文件"""

        if not data or not any(data.values()):

            print("没有数据可保存")

            return

            

        df = pd.DataFrame(data)

        df['value'] = df['value'].apply(lambda x: f"{x:.0f}万" if pd.notnull(x) else '-')

        df.to_csv(filename, index=False, encoding='utf-8-sig')

        print(f"数据已保存到 {filename}")

        

    def close(self):

        """关闭浏览器"""

        if self.driver:

            self.driver.quit()



def main():

    team_url = "https://www.tzuqiu.cc/teams/2/show.do"

    scraper = PlayerScraper()

    

    try:

        # 获取所有球员链接

        player_info = scraper.get_players_urls(team_url)

        print(f"找到 {len(player_info)} 名球员")

        

        all_data = {

            'player_name': [],

            'date': [],

            'value': [],

            'club': [],

            'age': []

        }

        

        # 遍历每个球员获取历史身价

        for player_url, player_name in player_info:

            try:

                player_data = scraper.get_player_history(player_url, player_name)

                if player_data:

                    for key in all_data:

                        all_data[key].extend(player_data[key])

                time.sleep(random.uniform(2, 4))

            except Exception as e:

                print(f"处理球员 {player_name} 时出错: {str(e)}")

                continue

        

        # 保存数据

        scraper.save_to_csv(all_data)

        

    except Exception as e:

        print(f"程序执行出错: {str(e)}")

    finally:

        scraper.close()



if __name__ == "__main__":

    main()