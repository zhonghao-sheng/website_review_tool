import os

# 获取特定环境变量，如果不存在则返回 'Not Set'

# rdsusername = os.environ.get('RDS_HOSTNAME', 'Not Set')
for key, value in os.environ.items():
    print(key, value)
