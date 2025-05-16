import pandas as pd
import os
import logging
import pymongo
from datetime import datetime
import json
from pymongo.errors import BulkWriteError, ConnectionFailure

class EASportsFCMongoImporter:
    def __init__(self, input_file=None, db_name='ea_sports_fc', collection_name='players'):
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # MongoDB配置
        self.mongo_uri = "mongodb://localhost:27017/"
        self.db_name = db_name
        self.collection_name = collection_name
        
        # 设置文件路径
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 如果未指定输入文件，尝试查找最新的清洗后文件
        if input_file is None:
            self.input_file = self.find_latest_cleaned_file()
        else:
            self.input_file = os.path.join(self.current_dir, input_file)
        
        # 检查输入文件是否存在
        if not os.path.exists(self.input_file):
            self.logger.error(f"输入文件不存在: {self.input_file}")
            raise FileNotFoundError(f"找不到文件: {self.input_file}")
        
        # 初始化MongoDB连接
        self.client = None
        self.db = None
        self.collection = None
        
        # 读取数据
        self.data = None
        self.load_data()
    
    def find_latest_cleaned_file(self):
        """查找最新的清洗后文件"""
        files = [f for f in os.listdir(self.current_dir) if f.startswith('ea_sports_fc_players_cleaned_') and f.endswith('.xlsx')]
        
        if not files:
            # 如果没有找到清洗后的文件，尝试使用原始文件
            original_file = os.path.join(self.current_dir, 'ea_sports_fc_players.xlsx')
            if os.path.exists(original_file):
                self.logger.warning("未找到清洗后的文件，将使用原始数据文件")
                return original_file
            else:
                self.logger.error("未找到任何可用的数据文件")
                raise FileNotFoundError("未找到任何可用的数据文件")
        
        # 按文件修改时间排序，获取最新的文件
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.current_dir, f)))
        self.logger.info(f"找到最新的清洗后文件: {latest_file}")
        return os.path.join(self.current_dir, latest_file)
    
    def load_data(self):
        """加载Excel数据"""
        try:
            self.data = pd.read_excel(self.input_file)
            self.logger.info(f"成功加载数据，共 {len(self.data)} 条记录")
        except Exception as e:
            self.logger.error(f"加载数据失败: {str(e)}")
            raise
    
    def connect_to_mongodb(self):
        """连接到MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # 检查连接
            self.client.server_info()
            
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.logger.info(f"成功连接到MongoDB: {self.db_name}.{self.collection_name}")
            
        except ConnectionFailure as e:
            self.logger.error(f"连接MongoDB失败: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"MongoDB操作出错: {str(e)}")
            raise
    
    def import_data(self, drop_existing=False):
        """导入数据到MongoDB"""
        if self.data is None or len(self.data) == 0:
            self.logger.error("没有数据可导入")
            return
        
        try:
            # 连接到MongoDB
            self.connect_to_mongodb()
            
            # 如果需要，删除现有集合
            if drop_existing:
                self.logger.info(f"删除现有集合: {self.collection_name}")
                self.collection.drop()
            
            # 转换数据为字典列表
            records = self.data.to_dict('records')
            
            # 添加导入时间戳
            import_time = datetime.now()
            for record in records:
                record['imported_at'] = import_time
                
                # 确保MongoDB中的_id不重复
                if 'Name' in record:
                    # 使用球员名称作为唯一标识符的一部分
                    record['_id'] = f"{record['Name']}_{import_time.strftime('%Y%m%d%H%M%S')}"
            
            # 批量插入数据
            result = self.collection.insert_many(records)
            self.logger.info(f"成功导入 {len(result.inserted_ids)} 条记录到MongoDB")
            
            # 创建索引
            self.logger.info("创建索引...")
            self.collection.create_index("Name")
            self.collection.create_index("OVR")
            self.collection.create_index("position_category")
            self.collection.create_index("rating_category")
            
            return len(result.inserted_ids)
            
        except BulkWriteError as e:
            self.logger.error(f"批量写入错误: {str(e.details)}")
            raise
        except Exception as e:
            self.logger.error(f"导入数据失败: {str(e)}")
            raise
        finally:
            if self.client:
                self.client.close()
    
    def export_collection_info(self):
        """导出集合信息"""
        try:
            self.connect_to_mongodb()
            
            # 获取集合统计信息
            stats = {
                "collection_name": self.collection_name,
                "document_count": self.collection.count_documents({}),
                "indexes": list(self.collection.index_information().keys()),
                "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 获取数据分布统计
            if "rating_category" in self.data.columns:
                rating_stats = self.data["rating_category"].value_counts().to_dict()
                stats["rating_distribution"] = rating_stats
            
            if "position_category" in self.data.columns:
                position_stats = self.data["position_category"].value_counts().to_dict()
                stats["position_distribution"] = position_stats
            
            # 保存统计信息到JSON文件
            stats_file = os.path.join(self.current_dir, f"mongodb_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"集合统计信息已保存到 {stats_file}")
            return stats
            
        except Exception as e:
            self.logger.error(f"导出集合信息失败: {str(e)}")
            raise
        finally:
            if self.client:
                self.client.close()

def main():
    try:
        importer = EASportsFCMongoImporter()
        importer.import_data(drop_existing=True)
        importer.export_collection_info()
    except Exception as e:
        logging.error(f"MongoDB导入过程出错: {str(e)}")

if __name__ == "__main__":
    main() 