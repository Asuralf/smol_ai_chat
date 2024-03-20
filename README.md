# Smol AI Chat 

基于`智谱 AI ` API 加了个UI。
PySide6 的练习作品。
## API Key 申请
[申请地址](https://www.free-api.com/doc/632)
## 使用方法
项目根目录下新建一个文件 `api_config.json`：
输入内容
```json
{
  "API_KEY": "your_api_key"
}
```

建议新建一个 venv
```shell
pip install -r requirement.txt
python chat.py
```

## 打包
windows 下
```
./pack.ps1
```
