import mysql.connector
from mysql.connector import pooling, Error
import yaml
from plugins.Waifu.cells.config import ConfigManager

class MySQLClient:
    def __init__(self, database_config: ConfigManager):
        mysql_config = database_config.data.get('mysql')
        host = mysql_config['host']
        user = mysql_config['user']
        password = mysql_config['password']
        database = mysql_config['database']
        pool_name = mysql_config['pool_name']
        pool_size = mysql_config['pool_size']
        self.connection_pool = None
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                host=host,
                user=user,
                password=password,
                database=database
            )
            print("成功创建连接池")
        except Error as e:
            print(f"连接池创建失败: {e}")

    def _fetch_data(self, query, params=None):
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"查询失败: {e}")
            return None
        finally:
            cursor.close()
            connection.close()  # 归还连接到连接池

    def _update_data(self, query, params=None):
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            print(f"成功更新 {cursor.rowcount} 行")
        except Error as e:
            print(f"更新失败: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()  # 归还连接到连接池
    
    # 获得所有表情包
    def fetch_all_emoji(self):
        query = "select * from TEmojiPack;"
        return self._fetch_data(query)
    
    # 获得FKeyword为key的表情包
    def fetch_emoji_by_key(self, keyword: str):
        query = "select * from TEmojiPack where FKeyword = %s"
        return self._fetch_data(query, [keyword])
    
    # 获得FUserId为user_id的用户信息
    def fetch_user_info(self, user_id: int):
        query = "select * from TUserProfile where FUserId = %s"
        user_info = self._fetch_data(query, [user_id])
        if not user_info:  # 处理 None 和空列表
            return None
        return user_info[0]

    # 扣除一点语音余额
    def decrement_voice_balance(self, user_id: int):
        query = "UPDATE TUserProfile SET FVoiceBalance = FVoiceBalance - 1 WHERE FUserId = %s"
        return self._update_data(query, [user_id])

    # 扣除一点文字余额
    def decrement_message_balance(self, user_id: int):
        query = "UPDATE TUserProfile SET FMessageBalance = FMessageBalance - 1 WHERE FUserId = %s"
        return self._update_data(query, [user_id])
