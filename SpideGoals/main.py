from premier_league_scraper import PremierLeagueScraper
from proxy_manager import ProxyManager
import time

def main():
    scraper = PremierLeagueScraper()
    proxy_manager = ProxyManager()
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 获取数据
            data = scraper.scrape_data()
            
            if data:
                # 保存数据
                scraper.save_to_excel(data)
                break
            
            # 如果失败，使用新的代理重试
            proxy = proxy_manager.get_random_proxy()
            if proxy:
                scraper.headers['proxy'] = proxy
            
            retry_count += 1
            time.sleep(5)  # 等待5秒后重试
            
        except Exception as e:
            print(f"Error: {str(e)}")
            retry_count += 1
            time.sleep(5)

if __name__ == "__main__":
    main() 