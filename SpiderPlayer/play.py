import pandas as pd
from bs4 import BeautifulSoup
import logging
import os
import glob

class FootballPlayerSpider:
    def __init__(self):
        self.players_data = []
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('spider.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def parse_player_info(self, tr_element):
        """解析单个球员信息"""
        try:
            # 获取所有的td元素
            tds = tr_element.find_all('td')
            if not tds or len(tds) < 12:
                return None

            # 获取球员基本信息
            player_td = tds[1]
            name_div = player_td.find('div', class_='limittext')
            name = name_div.get_text(strip=True) if name_div else ''
            
            # 获取球队、年龄和位置信息
            sub_title = player_td.find('span', class_='sm_logo-name subTitle')
            if sub_title:
                info_text = sub_title.get_text(strip=True)
                info_parts = [x.strip() for x in info_text.split(',') if x.strip()]
                
                team = info_parts[0] if len(info_parts) > 0 else ''
                age = info_parts[1] if len(info_parts) > 1 else ''
                position = info_parts[2] if len(info_parts) > 2 else ''
            else:
                team = age = position = ''

            # 获取其他统计数据
            appearances = tds[2].get_text(strip=True)
            minutes = tds[3].get_text(strip=True)
            goals = tds[4].get_text(strip=True)
            assists = tds[5].get_text(strip=True)
            
            # 获取红黄牌
            cards_td = tds[6]
            yellow_card = cards_td.find('span', class_='yel-card')
            red_card = cards_td.find('span', class_='red-card')
            yellow_cards = yellow_card.get_text(strip=True) if yellow_card else '0'
            red_cards = red_card.get_text(strip=True) if red_card else '0'
            
            # 其他数据
            pass_success = tds[7].get_text(strip=True)
            chances_created = tds[8].get_text(strip=True)
            aerial_won = tds[9].get_text(strip=True)
            rating = tds[11].get_text(strip=True)

            return {
                '球员': name,
                '俱乐部': team,
                '年龄': age,
                '位置': position,
                '出场': appearances,
                '上场时间': minutes,
                '进球': goals,
                '助攻': assists,
                '黄牌': yellow_cards,
                '红牌': red_cards,
                '传球成功率': pass_success,
                '创造机会': chances_created,
                '争顶成功': aerial_won,
                '评分': rating
            }
            
        except Exception as e:
            self.logger.error(f"解析球员信息出错: {str(e)}")
            return None

    def parse_html_file(self, html_path):
        """从HTML文件中解析数据"""
        try:
            # 读取HTML文件
            self.logger.info(f"正在读取HTML文件: {os.path.basename(html_path)}")
            with open(html_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # 解析HTML内容
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找球员数据表格
            table = soup.find('table', {'id': 'playerStatSummary'})
            if table:
                player_rows = table.find('tbody').find_all('tr')
                if player_rows:
                    self.logger.info(f"从HTML文件中找到 {len(player_rows)} 条记录")
                    
                    # 解析每个球员数据
                    page_data = []
                    for row in player_rows:
                        player_info = self.parse_player_info(row)
                        if player_info:
                            page_data.append(player_info)
                    
                    if page_data:
                        # 将新数据添加到现有数据中
                        self.players_data.extend(page_data)
                        self.logger.info(f"成功解析 {len(page_data)} 条球员数据")
                        # 保存更新后的数据
                        self.save_to_csv()
                    else:
                        self.logger.warning("未能解析出任何球员数据")
                else:
                    self.logger.warning("找到表格但没有球员数据")
            else:
                self.logger.warning("未找到球员数据表格")
            
        except Exception as e:
            self.logger.error(f"解析HTML文件出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def save_to_csv(self):
        """保存数据到CSV文件，支持追加模式"""
        try:
            if not self.players_data:
                self.logger.warning("没有数据可供保存")
                return

            self.logger.info(f"准备保存 {len(self.players_data)} 条数据")
            df = pd.DataFrame(self.players_data)
            file_path = 'football_players.csv'
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                existing_df = pd.read_csv(file_path, encoding='utf-8-sig')
                # 合并现有数据和新数据，删除重复项
                df = pd.concat([existing_df, df]).drop_duplicates(subset=['球员', '俱乐部'], keep='last')
            
            # 保存文件
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"数据已保存，当前共有 {len(df)} 条记录")
            
        except Exception as e:
            self.logger.error(f"保存CSV文件出错: {str(e)}")

def main():
    spider = FootballPlayerSpider()
    
    # 指定HTML文件所在的文件夹路径
    html_folder = r"C:\Users\33622\Desktop\Spider\SpiderPlayer\html_path"
    
    # 获取文件夹中所有的HTML文件
    html_files = glob.glob(os.path.join(html_folder, "*.html"))
    
    if not html_files:
        print(f"在 {html_folder} 中未找到HTML文件")
        return
        
    print(f"找到 {len(html_files)} 个HTML文件")
    
    # 处理每个HTML文件
    for html_file in html_files:
        print(f"正在处理文件: {os.path.basename(html_file)}")
        spider.parse_html_file(html_file)
    
    # 显示最终结果
    if spider.players_data:
        print(f"所有文件处理完成，共收集 {len(spider.players_data)} 条记录")
    else:
        print("未能收集到任何数据")

if __name__ == "__main__":
    main()
