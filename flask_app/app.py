from flask import Flask, render_template, request, redirect, url_for, jsonify,send_file
from scripts import details,tools,exchange
from scripts.login import get_qr_url, check_login, ReturnTotalCookie,show_qrcode
import json
import os
import global_vars
from concurrent.futures import ThreadPoolExecutor
import asyncio
from concurrent.futures import ThreadPoolExecutor
from scripts.log import log_message, setup_logger
from collections import defaultdict




tasks = {}
executor = ThreadPoolExecutor(max_workers=1)
app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(base_dir)
goodslist_path = os.path.join(base_dir, 'goodslist.json')
config_path = os.path.join(base_dir, 'config.json')
tasklistpath = os.path.join(base_dir, 'tasklist.json')

"""
log_message
所有的报错信息为英文
成功信息为中文
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_log')
def view_log():
    log_path = os.path.join(app.root_path, 'log.log')
    return send_file(log_path, mimetype='text/plain')

#####################
#开始任务#
#####################

@app.route('/start_task', methods=['GET', 'POST'])
async def start_task():
    try:
        with open(tasklistpath, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            log_message("成功读取任务清单")
    except Exception as e:
        log_message(f"Error loading tasklist.json: {e}")
        return redirect(url_for('create_task', alert="请先创建任务清单"))

    return render_template('start_task.html', tasks=tasks, current_time=await exchange.get_ntp_time(),task_running=global_vars.task_running)

@app.route('/get_current_time')
async def get_current_time():
    ntp_time = await exchange.get_ntp_time()
    if ntp_time is not None:
        formatted_time = ntp_time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        formatted_time = "Error fetching NTP time"
    
    return jsonify(current_time=formatted_time)

@app.route('/get_task_status', methods=['GET'])
def get_task_status():
    return jsonify(task_running=global_vars.task_running)



def run_asyncio_task(task_name,count):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(exchange.schedule_task(task_name,count))
    loop.close()

@app.route('/run_task', methods=['POST'])
def run_task():
    with open(tasklistpath, 'r', encoding="utf-8") as f:
        tasks = json.load(f)
    selected_task_time = request.form.get('task')
    selected_task = next((task for task in tasks if task['time'] == selected_task_time), None)
    
    if selected_task:
        count = selected_task.get('count', 5)  # 默认值为1，如果count不存在
        try:
            count = int(count)
        except Exception as e:
            log_message(f"Error converting count to integer: {e}")
            log_message(f"自动改成默认值count: {count}")
            count = 5
        log_message(f"任务已经开始: {selected_task.get('name')}")
        global_vars.task_running = True
        executor.submit(run_asyncio_task, selected_task, count)
        return "Task is running"
    else:
        return "Task not found", 404



@app.route('/get_task_messages', methods=['GET'])
def get_task_messages():
    # 获取并清理任务消息
    messages = exchange.task_messages.copy()
    exchange.task_messages.clear()
    return jsonify(messages=messages)

# 停止任务
@app.route('/stop_task', methods=['POST'])
def stop_task():
    global_vars.task_running = False
    messages = "任务已经停止"
    log_message(messages)
    return jsonify(messages=messages)

#####################
#获取个人信息
#####################

@app.route('/get_user_info')
def get_user_info():
    alert = request.args.get('alert')
    # 获取二维码 URL
    qr_url, app_id, ticket, device = get_qr_url()
    # 使用 login.py 中的 show_qrcode 生成并保存二维码图片
    qr_image_path = os.path.join(base_dir, "static/code.png")
    qr_image_url = url_for('static', filename='code.png')
    show_qrcode(qr_url)
    log_message(f"二维码已成功保存在:{qr_image_path}")

    if alert:
        return render_template('get_user_info.html', qr_image_url=qr_image_url, app_id=app_id, ticket=ticket, device=device, alert=alert)
    else:
        return render_template('get_user_info.html', qr_image_url=qr_image_url, app_id=app_id, ticket=ticket, device=device)


@app.route('/check_qr_login', methods=['POST'])
def check_qr_login():
    app_id = request.json.get('app_id')
    ticket = request.json.get('ticket')
    device = request.json.get('device')
    log_message(f"app_id:{app_id},ticket:{ticket},device:{device}")

    if not app_id or not ticket or not device:
        return jsonify({'status': 'error', 'message': 'Missing required parameters'}), 400

    try:
        # Check QR code login status
        uid, game_token = check_login(app_id, ticket, device)
        if not uid or not game_token:
            log_message(f"Invalid login credentials: {uid}, {game_token}")
            return jsonify({'status': 'error', 'message': 'Invalid login credentials'}), 401

        cookie = ReturnTotalCookie(uid, game_token, ticket)
        if not cookie:
            log_message(f"Failed to generate cookie")
            return jsonify({'status': 'error', 'message': 'Failed to generate cookie'}), 500

        # Convert cookie dictionary to a string
        cookie_str = tools.format_cookie_string(cookie)
        global_vars.cookie_str = cookie_str
        # 创建单独项的 cookie 列表
        cookies_list = [{key: value} for key, value in cookie.items()]
        global_vars.cookie_stored = cookies_list

         # Write the cookie to config.json
        config_data = {'cookie': cookie_str,"cookies_list": cookies_list, "device_id": global_vars.device_id}
        log_message("成功把cookie写入config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            
            json.dump(config_data, f)

        return jsonify({'status': 'success', 'cookie': cookie_str})

    except Exception as e:
        log_message(f"An error occurred during QR login check: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500




#####################
#获取商品列表
#####################
@app.route('/product_list', methods=['GET', 'POST'])
def product_list_view():
    products = []
    golds=details.get_point(global_vars.cookie_str)
    if request.method == 'POST':
        selected_category = request.form.get('category')
        global_vars.game_biz = selected_category
        products = details.get_goods_list(selected_category, global_vars.cookie_str)
        
    return render_template('product_list.html', products=products, game_biz=global_vars.game_biz,golds=golds)
#添加到心愿单
@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    product_id = request.form.get('product_id')
    product_time = request.form.get('product_time')
    product_name = request.form.get('product_name')
    product_biz = request.form.get('product_biz')

    # 使用 tools.py 中的 add_to_wishlist 函数
    tools.add_to_wishlist(product_name,product_id, product_time,product_biz)
    log_message(f"商品已经添加到备选清单:  {product_name}")
    return jsonify({'status': 'success', 'message': '已成功添加到备选清单'})


# 删除心愿单中的商品
@app.route('/clear_wishlist', methods=['POST'])
def clear_wishlist():
    tools.clear_goodslist()
    log_message("备选清单已经清空")
    return jsonify({"message": "备选清单已经清空"}), 200



#####################
#新建任务
#####################

@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'GET':
        # 检查是否已登录
        if not global_vars.cookie_str:
            # 未登录则重定向到登录页面
            return redirect(url_for('get_user_info', alert="请先登录"))
        # 获取地址数据
        address_data = details.getaddress(global_vars.cookie_str)
        log_message(f"成功获取地址")
        # 尝试读取商品清单
        try:
            with open(goodslist_path, 'r', encoding='utf-8') as f:
                goods_list = json.load(f)
        except json.JSONDecodeError as e:
            # 处理JSON解码错误
            log_message(f"Error decoding JSON from {goodslist_path}: {e}")
            goods_list = []

        # 尝试获取地址列表
        try:
            addresses = address_data.get('data', {}).get('list', [])
            if not addresses:
                # 如果没有找到地址，抛出异常
                raise ValueError("No addresses found in the provided data.")
        except KeyError as e:
            # 处理键错误
            log_message(f"Key error accessing address data: {e}")
            addresses = []
        except ValueError as e:
            # 处理未找到地址的情况
            log_message(f"Value error: {e}")
            addresses = []
        except Exception as e:
            # 处理其他未预期的错误
            log_message(f"Unexpected error when accessing address data: {e}")
            addresses = []
        addresses.append({'id': '', 'addr_ext': '空地址，兑换游戏内商品选这个'})

        print(addresses)
        # 设置默认时间
        default_time = goods_list[0]['time'] if goods_list else ''
        # 渲染创建任务的页面
        return render_template('create_task.html', addresses=addresses, goods_list=goods_list, default_time=default_time)
    
    




#新建任务清单 starttask从任务清单里面读取
@app.route('/add_to_tasklist', methods=['POST'])
def add_to_tasklist():
    try:
        # 尝试从 config.json 获取 cookies
        cookies = tools.get_cookies_from_config()
        uid = cookies.get('account_id')
        device_id = cookies.get('device_id')
        cookie = tools.get_cookiestr_from_config()
        if not uid or not device_id:
            raise ValueError("config.json 中的 cookies 缺少必要的 account_id 或 device_id")

    except Exception as e:
        log_message(f"Error retrieving account_id or device_id from config.json: {e}")
        # 从 config.json 获取失败，尝试从 global_vars 获取
        try:
            
            for cookie_dict in global_vars.cookie_stored:
                if 'account_id' in cookie_dict:
                    uid = cookie_dict['account_id']
                    break
            cookie = global_vars.cookie_str
            device_id = global_vars.device_id
        except IndexError:
            log_message(f"Error retrieving account_id or device_id from global_vars: {e}")
            return jsonify({'status': 'error', 'message': '无法获取用户ID和设备ID'}), 500

    # 从请求中获取其他参数
    goods_id = request.json.get('goods_id')
    address_id = request.json.get('address')
    time = request.json.get('task_time')
    name = request.json.get('task_name')
    count = request.json.get('count')
    game_biz = request.json.get('biz')


    if not goods_id or not address_id or not time or not name or not game_biz or not count:
        log_message("Missing required parameters")
        return jsonify({'status': 'error', 'message': '请求数据缺失'}), 400

    try:
        tools.add_to_tasklist(goods_id, uid, game_biz, address_id, device_id, cookie, time, name,count)
        log_message(f"Task added successfully: {name}")
        return jsonify({'status': 'success', 'message': '已成功添加到任务清单'})
    except Exception as e:
        log_message(f"Error adding task: {e}")
        return jsonify({'status': 'error', 'message': f'添加任务时发生错误: {str(e)}'}), 500


# 删除任务清单中的任务
@app.route('/clear_tasklist', methods=['POST'])
def clear_tasklist():
    tools.clear_tasklist()
    log_message("任务清单已经清空")
    return jsonify({"message": "任务清单已经清空"}), 200










#####################
#入口
#####################

def load_config():
    """
    从 config.json 文件中加载 cookie 和 device
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            global_vars.cookie_str = config['cookie']
            global_vars.device_id = config['device_id']
            log_message("成功读取config.json")
        
    except Exception as e:
        print(f"None Cookie Exists: {e}")

if __name__ == '__main__':
    setup_logger() 
    # 检查 goodslist.json 是否存在，不存在则创建  不然会报错
    if not os.path.exists(goodslist_path):
        with open(goodslist_path, 'w') as f:
            json.dump([], f)  
        log_message(f"goodlist不存在，已创建文件：{goodslist_path}")

    log_message("Test log message")
    load_config()
    app.run(debug=True)