import hashlib
import time

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import logging
import os
import json

# logging.basicConfig(level=logging.INFO, stream=sys.stdout)


# 计算某个文件的md5值
def md5sum(file_name):
    fo = open(file_name, 'rb')
    file_content = fo.read()
    fo.close()
    m = hashlib.md5(file_content)
    file_md5 = m.hexdigest()

    return file_md5


# 获取基本配置
user_home = os.path.expanduser('~')
cos_upload_config_filename = os.path.join(user_home, 'Documents', 'cos_upload_config.json')
cos_upload_config_file = open(cos_upload_config_filename, 'r')
cos_upload_config_str = cos_upload_config_file.read()
cos_upload_config = json.loads(cos_upload_config_str)

secret_id = cos_upload_config['secret_id']  # 替换为用户的 secretId
secret_key = cos_upload_config['secret_key']  # 替换为用户的 secretKey
region = cos_upload_config['region']  # 替换为用户的 Region
bucket = cos_upload_config['bucket']
local_path = cos_upload_config['local_path']
token = None  # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

# 获取客户端对象
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)

# 查询存储桶下的全部对象列表
contents = []
marker = ""
while True:
    response = client.list_objects(
        Bucket=bucket,
        Prefix='',
        Marker=marker
    )
    contents = contents + response['Contents']
    if response['IsTruncated'] == 'false':
        break
    marker = response['NextMarker']

# 把对象元数据中key和etag生成map
cos_filename_etag_map = {}
for content in contents:
    key = content['Key']
    etag = str(content['ETag'])
    etag = etag.strip('"')
    cos_filename_etag_map[key] = etag

# 获取本地文件夹下所有文件
local_files = []
if not os.path.exists(local_path):
    print("ERROR: 本地路径不存在")
for root, dirs, names in os.walk(local_path):
    for filename in names:
        local_files.append(os.path.join(root, filename))

# 通过比较md5判断文件是否有更新，上传本地已更新的文件和新添加的文件
upload_files = []
for file in local_files:
    obs_path = file[len(local_path)+len(os.sep):]
    obs_path = obs_path.replace('\\', '/')
    if obs_path not in cos_filename_etag_map:
        upload_files.append(file)
    elif md5sum(file) != cos_filename_etag_map[obs_path]:
        upload_files.append(file)

# 删除本地不存在的文件
delete_files = []
cos_files = cos_filename_etag_map.keys()
for cos_file in cos_files:
    cos_file = str(cos_file)
    cos_file = cos_file.replace('/', '\\')
    abs_path = os.path.join(local_path, cos_file)
    if abs_path not in local_files:
        delete_files.append(cos_file)

# 执行上传操作
for upload_file in upload_files:
    obs_path = upload_file[len(local_path)+len(os.sep):]
    obs_path = obs_path.replace('\\', "/")
    client.upload_file(
        Bucket=bucket,
        Key=obs_path,
        LocalFilePath=upload_file,
        EnableMD5=False
    )
    print(upload_file + '   上传成功')

# 执行删除操作
for delete_file in delete_files:
    client.delete_object(
        Bucket=bucket,
        Key=delete_file
    )
    print(delete_file + '   删除成功')

print('执行完成！')
