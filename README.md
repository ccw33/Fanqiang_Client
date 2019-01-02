# 说明
这是一个fanqiang客户端
# 开发
## 安装依赖
pip install -r requirements.txt
## 运行
python Client.py

# 生产
## 打包
- pyinstaller -F --icon=google_60px_26051_easyicon.net.ico Client.py --noconsole
- 然后复制Privoxy和log文件夹到dist目录下
## 使用
双击Client.exe