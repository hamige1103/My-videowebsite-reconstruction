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

# 检查所有电影类型
cursor.execute('SELECT DISTINCT type_name FROM sakura_movdetail')
types = cursor.fetchall()
print('数据库中存在的电影类型:')
for t in types:
    print(f'  {t[0]}')

# 检查是否有包含'动作'的类型
cursor.execute("SELECT COUNT(*) FROM sakura_movdetail WHERE type_name LIKE '%动作%'")
action_count = cursor.fetchone()[0]
print(f'\n包含"动作"的电影数量: {action_count}')

# 查看前5部电影的类型和名称
cursor.execute('SELECT vod_id, vod_name, type_name FROM sakura_movdetail LIMIT 5')
print('\n前5部电影信息:')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, 名称: {row[1]}, 类型: {row[2]}')

cursor.close()
conn.close()