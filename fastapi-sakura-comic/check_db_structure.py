import sqlite3

# 连接数据库
conn = sqlite3.connect('sakura_comic.db')
cursor = conn.cursor()

# 检查表结构
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'  - {table[0]}')

# 检查sakura_movdetail表结构
cursor.execute("PRAGMA table_info(sakura_movdetail)")
columns = cursor.fetchall()
print('\nsakura_movdetail表结构:')
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

# 检查一些示例数据
cursor.execute("SELECT vod_name, vod_type, vod_class FROM sakura_movdetail LIMIT 5")
rows = cursor.fetchall()
print('\n示例数据:')
for row in rows:
    print(f'  - 名称: {row[0]}, 类型: {row[1]}, 分类: {row[2]}')

# 检查动作电影相关的数据
cursor.execute("SELECT vod_name, vod_type, vod_class FROM sakura_movdetail WHERE vod_class LIKE '%动作%' OR vod_name LIKE '%动作%' LIMIT 5")
rows = cursor.fetchall()
print('\n动作电影相关数据:')
for row in rows:
    print(f'  - 名称: {row[0]}, 类型: {row[1]}, 分类: {row[2]}')

conn.close()