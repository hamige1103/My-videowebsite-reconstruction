import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root', 
    password='123456',
    database='movie',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 检查sakura_movdetail表结构
cursor.execute('DESCRIBE sakura_movdetail')
columns = cursor.fetchall()
print('sakura_movdetail表结构:')
for col in columns:
    print(f'  - {col[0]} ({col[1]})')

# 检查一些动作电影示例
cursor.execute("SELECT vod_id, vod_name, type_name, vod_class FROM sakura_movdetail WHERE type_name LIKE '%动作%' LIMIT 3")
rows = cursor.fetchall()
print('\n动作电影示例:')
for row in rows:
    print(f'  - ID: {row[0]}, 名称: {row[1]}, 类型: {row[2]}, 分类: {row[3]}')

cursor.close()
conn.close()