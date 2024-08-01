
# Mys Goods GUI

一个基于Python、Flask和Electron的桌面应用，用于自动兑换米游社商品。

## 写在前面

感谢你使用Mys Goods GUI。由于本人能力有限，项目可能仍然存在一些bug，欢迎提交issue，也请勿将本项目用于非法用途。希望这个项目对你有所帮助，并且欢迎提出改进建议。

## Todolist

### 功能开发

- [ ] 优化ui界面
- [ ] 增加一键打包的脚本
- [ ] 增加多用户功能
- [x] 处理登录逻辑
- [x] 处理任务停止和重新开始
- [x] 增加自定义兑换时post次数的选项

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
    │  |  login_stoken.py     使用游戏二维码登陆获取stoken等数据(已弃用)
    │  │  tools.py     写入和读取json
    │  │  __init__.py
    │  │
    │  └─__pycache__
    │        
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

### 普通用户

- 直接在 release 页面下载最新版本即可。

### 开发者

#### 先决条件

- Python 
- Node.js 

#### 安装步骤

1. 克隆本仓库：

    ```bash
    git clone https://github.com/mxyooR/Mys_Goods_Gui
    cd Mys_Goods_Gui
    ```

2. 安装 Python 依赖：

    ```bash
    cd flask_app
    pip install -r requirements.txt
    ```

3. 安装 Electron 依赖：

    ```bash
    cd ..
    npm install
    ```

#### 运行应用

1. 启动 Flask 后端：

    ```bash
    cd flask_app
    python app.py
    ```
    若无需 Electron，可直接在浏览器打开 `127.0.0.1:5000`

2. 启动 Electron 前端：

    ```bash
    cd ..
    npm start
    ```

3. 打包应用(option)：
    ```bash
    cd flask_app
    pyinstaller.exe app.spec
    cd ..
    npm run package
    ```

#### 开发文档

[develop](/docs/develop.md)

## 参考项目

本项目参考了以下开源项目：

- [mihoyo_login](https://github.com/Womsxd/mihoyo_login)
- [nonebot-plugin-mystool](https://github.com/Ljzd-PRO/nonebot-plugin-mystool)
- [Mys-Exchange-Goods](https://github.com/GOOD-AN/Mys-Exchange-Goods)
- [mihoyo-api-collect](https://github.com/UIGF-org/mihoyo-api-collect)
- [MihoyoBBSTools](https://github.com/Womsxd/MihoyoBBSTools)

## 注意事项
- 由于日志输出使用的是电脑时间，而兑换时间使用的是 NTP 时间，所以日志上的时间会有所偏差。

## 免责声明

- 本 Mys Goods GUI 程序（以下简称“程序”）由用户编写，仅供学习和研究目的使用。在使用本程序前，请仔细阅读以下免责声明：

1. **使用风险**  
   使用本程序的风险由用户自行承担。程序的开发者不对因使用或无法使用本程序而产生的任何直接或间接损失承担任何责任。

2. **合法性**  
   用户在使用本程序时应遵守相关法律法规及服务提供商的使用条款。程序的开发者不对用户因使用本程序而违反任何法律法规或服务条款承担责任。

3. **责任限制**  
   在适用法律允许的最大范围内，程序的开发者不对因使用或无法使用本程序而导致的任何损害承担责任，包括但不限于利润损失、数据丢失或业务中断等。

通过下载、安装或使用本程序，用户即表示已阅读、理解并同意本免责声明的所有条款。如果用户不同意本免责声明中的任何条款，请不要使用本程序。
同意本免责声明的所有条款。如果用户不同意本免责声明中的任何条款，请不要使用本程序。

