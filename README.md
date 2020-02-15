# cosupload
虽然把博客放在github很方便，也是免费的，但是国内访问不定时抽风，所以选择了把博客放在腾讯云对象存储上。

于是我就写了这个工具，通过对比md5的方式上传更新和删除的文件到腾讯云cos。

在windows平台下可以直接下载`dist`目录下的`cosupload.exe`，然后将`cos_upload_config.json`复制到`C:\Users\xxxx\Documents`下，修改配置项，就可以直接运行了。
```json
{
    "secret_id": "",    // 腾讯云用户的secret_id
    "secret_key": "",   // 腾讯云用户的secret_key
    "region": "ap-shanghai",    // 对象存储桶的区域
    "bucket": "hugo-4382904721",    // 存储桶的bucket_id
    "local_path": "D:\\Hugo\\public"    // 本地需要上传的文件夹路径
}
```

如果有其他的需求可以修改代码，引入`requirements.txt`中的依赖后，执行`pyinstaller -F cosupload.py`就可以生成新的exe文件。

因为腾讯云对象存储路径分隔符是`/`，而windows下路径分割符为`\\`，所以在代码里做了一些手工的处理，使用macos和linux的朋友需要自己修改一下代码。