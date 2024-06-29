
# Mys Goods GUI

一个基于Python、Flask和Electron的桌面应用，用于自动兑换米游社商品。

## 项目结构

```
│  main.js            electron主文件  
│  package-lock.json
│  package.json       打包成exe的配置文件
│  preload.js
│  README.md
│  tray_icon.ico      图标
│  tray_icon.png      图标
│
└─flask_app
    │  app.py          flask主文件
    │  global_vars.py  全局变量
    │  goodslist.json  备选清单
    │  log.log         日志
    │  __init__.py
    │
    ├─scripts
    │  │  details.py   获取地址、商品信息
    │  │  exchange.py  兑换主代码
    │  │  log.py       日志功能
    │  │  login.py     登录功能
    │  │  tools.py     写入和读取json
    │  │  __init__.py
    │  │
    │  └─__pycache__
    │          details.cpython-311.pyc
    │          exchange.cpython-311.pyc
    │          log.cpython-311.pyc
    │          login.cpython-311.pyc
    │          tools.cpython-311.pyc
    │
    ├─static
    │  │  code.png
    │  │
    │  └─css
    │          styles.css
    │
    └─templates
            base.html          
            create_task.html      新建任务
            get_user_info.html    获取个人信息
            index.html            主界面
            product_list.html     获取商品信息
            start_task.html       开始任务
```

## 安装与运行

### 先决条件

- Python 
- Node.js 

### 安装步骤

1. 克隆本仓库：

    ```bash
    git clone https://github.com/mxyooR/Mys_Goods_Gui
    cd Mys_Goods_Gui
    ```

2. 设置Python虚拟环境并安装依赖：

    ```bash
    python -m venv venv
    source venv/bin/activate  # 对于Windows用户，使用 `venv\Scriptsctivate`
    pip install -r requirements.txt
    ```

3. 安装Electron依赖：

    ```bash
    cd electron
    npm install
    ```

### 运行应用

1. 启动Flask后端：

    ```bash
    cd ..
    flask run
    ```

2. 启动Electron前端：

    ```bash
    cd electron
    npm start
    ```

## 参考项目

本项目参考了以下开源项目：

- (https://github.com/Womsxd/mihoyo_login)
- [Ljzd-PRO/nonebot-plugin-mystool](https://github.com/Ljzd-PRO/nonebot-plugin-mystool)

## 注意

由于本人能力有限，项目可能仍然存在很多bug，欢迎提交issue 仅供学习使用，请勿用于非法用途
