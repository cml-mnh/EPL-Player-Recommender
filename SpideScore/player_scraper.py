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
                
                players = []
                # 等待球员表格加载，使用更具体的选择器
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr"))
                )
                
                # 获取所有球员行，使用更精确的选择器
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table.table tbody tr[role='row']")
                
                if not rows:
                    print("未找到球员列表，重试...")
                    retry_count += 1
                    continue
                
                for row in rows:
                    try:
                        # 使用JavaScript获取元素，避免可能的可见性问题
                        player_info = self.driver.execute_script("""
                            var row = arguments[0];
                            var link = row.querySelector('td.text-left a');
                            var nameDiv = row.querySelector('td.text-left a div.limittext');
                            if (link && nameDiv) {
                                return {
                                    'link': link.href,
                                    'name': nameDiv.textContent.trim()
                                };
                            }
                            return null;
                        """, row)
                        
                        if player_info:
                            players.append((player_info['link'], player_info['name']))
                    except Exception as e:
                        print(f"获取球员链接时出错: {str(e)}")
                        continue
                
                if players:
                    return players
                
                print("未获取到任何球员信息，重试...")
                retry_count += 1
                
            except Exception as e:
                print(f"尝试 {retry_count + 1}/{max_retries} 失败: {str(e)}")
                retry_count += 1
                time.sleep(5)
        
        raise Exception("获取球员链接失败，已达到最大重试次数")
    
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
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 检查是否有身价图表
                chart_data = self.driver.execute_script("""
                    try {
                        // 等待Highcharts对象加载
                        if (typeof Highcharts === 'undefined') {
                            return {'error': 'Highcharts not loaded'};
                        }
                        
                        // 查找所有图表
                        var charts = document.querySelectorAll('.highcharts-container');
                        if (!charts.length) {
                            return {'error': 'No charts found'};
                        }
                        
                        // 遍历所有图表寻找身价图表
                        var valueData = null;
                        for (var i = 0; i < Highcharts.charts.length; i++) {
                            var chart = Highcharts.charts[i];
                            if (!chart) continue;
                            
                            var series = chart.series[0];
                            if (!series) continue;
                            
                            // 检查是否是身价图表
                            if (series.options && 
                                (series.options.fillColor && series.options.fillColor.indexOf('rgba(39,174,96') !== -1 ||
                                 series.options.color === '#27AE60')) {
                                
                                valueData = [];
                                var points = series.points;
                                var categories = chart.xAxis[0].categories;
                                
                                for (var j = 0; j < points.length; j++) {
                                    var point = points[j];
                                    valueData.push({
                                        date: categories[j],
                                        value: point.y
                                    });
                                }
                                break;
                            }
                        }
                        
                        return valueData ? {'data': valueData} : {'error': 'No value chart found'};
                    } catch (e) {
                        return {'error': e.toString()};
                    }
                """)
                
                if chart_data.get('error'):
                    print(f"获取 {player_name} 图表数据失败: {chart_data['error']}")
                    retry_count += 1
                    time.sleep(2)
                    continue
                
                if not chart_data.get('data'):
                    print(f"未找到 {player_name} 的身价数据")
                    return None
                
                # 整理数据
                data = {
                    'player_name': [],
                    'date': [],
                    'value': [],
                    'club': [],
                    'age': []
                }
                
                for point in chart_data['data']:
                    data['player_name'].append(player_name)
                    data['date'].append(point['date'])
                    value = point['value']
                    if value is not None:
                        value = float(value) / 10000  # 转换为万
                    data['value'].append(value)
                    data['club'].append('')  # 暂不获取俱乐部信息
                    data['age'].append('')   # 暂不获取年龄信息
                
                return data
                
            except Exception as e:
                print(f"尝试获取 {player_name} 身价数据时失败 {retry_count + 1}/{max_retries}: {str(e)}")
                retry_count += 1
                time.sleep(5)
        
        print(f"获取球员 {player_name} 身价数据失败，跳过")
        return None
    
    def save_to_csv(self, data, filename='player_values.csv'):
        """保存数据到CSV文件"""
        df = pd.DataFrame(data)
        # 将身价值格式化为"xx万"的形式
        df['value'] = df['value'].apply(lambda x: f"{x:.0f}万" if pd.notnull(x) else '-')
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
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
                    # 将数据添加到总数据中
                    for key in all_data:
                        all_data[key].extend(player_data[key])
                    print(f"成功获取 {player_name} 的数据")
                
                time.sleep(random.uniform(1, 3))  # 随机延迟
            except Exception as e:
                print(f"处理球员 {player_name} 时出错: {str(e)}")
                continue
        
        # 保存数据
        scraper.save_to_csv(all_data)
        print("数据已保存到 player_values.csv")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 