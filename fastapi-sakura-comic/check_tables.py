import sqlite3

# 连接数据库
conn = sqlite3.connect('sakura_comic.db')
cursor = conn.cursor()

# 检查所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('数据库中的所有表:')
for table in tables:
    print(f'  - {table[0]}')

# 检查每个表的结构
for table in tables:
    table_name = table[0]
    print(f'\n{table_name} 表结构:')
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f'  - {col[1]} ({col[2]})')

conn.close()