import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'config', 'pb_bi.db')

def migrate_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("检查 data_flows 表结构...")
        cursor.execute("PRAGMA table_info(data_flows)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"现有列: {columns}")
        
        if 'user_id' not in columns:
            print("添加 user_id 列...")
            cursor.execute("ALTER TABLE data_flows ADD COLUMN user_id INTEGER")
        
        if 'is_private' not in columns:
            print("添加 is_private 列...")
            cursor.execute("ALTER TABLE data_flows ADD COLUMN is_private INTEGER NOT NULL DEFAULT 0")
        
        if 'private_api_url' not in columns:
            print("添加 private_api_url 列...")
            cursor.execute("ALTER TABLE data_flows ADD COLUMN private_api_url TEXT")
        
        print("\n检查 data_snapshots 表结构...")
        cursor.execute("PRAGMA table_info(data_snapshots)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"现有列: {columns}")
        
        if 'user_id' not in columns:
            print("添加 user_id 列...")
            cursor.execute("ALTER TABLE data_snapshots ADD COLUMN user_id INTEGER")
        
        print("\n检查 dashboards 表结构...")
        cursor.execute("PRAGMA table_info(dashboards)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"现有列: {columns}")
        
        if 'user_id' not in columns:
            print("添加 user_id 列...")
            cursor.execute("ALTER TABLE dashboards ADD COLUMN user_id INTEGER")
        
        conn.commit()
        print("\n数据库迁移完成！")
        
        print("\ndata_flows 表最终结构:")
        cursor.execute("PRAGMA table_info(data_flows)")
        for col in cursor.fetchall():
            print(col)
        
        print("\ndata_snapshots 表最终结构:")
        cursor.execute("PRAGMA table_info(data_snapshots)")
        for col in cursor.fetchall():
            print(col)
        
        print("\ndashboards 表最终结构:")
        cursor.execute("PRAGMA table_info(dashboards)")
        for col in cursor.fetchall():
            print(col)
        
    except Exception as e:
        print(f"迁移失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
