import json
import os


# 获取当前文件的绝对路径
base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(base_dir)
goodslist_path = os.path.join(parent_dir, 'goodslist.json')
config_path = os.path.join(parent_dir, 'config.json')
tasklistpath = os.path.join(parent_dir, 'tasklist.json')

def add_to_wishlist(product_name,product_id, product_time,product_biz):
    """
    将商品添加到备选清单中
    """
    try:
        with open(goodslist_path, 'r', encoding='utf-8') as f:
            goods_list = json.load(f)
            print(goods_list)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Failed to read goodslist.json")
        goods_list = []

    # 添加新商品到备选清单
    new_item = {
        "name": product_name,
        "id": product_id,
        "time": product_time,
        "biz":product_biz
    }
    goods_list.append(new_item)

    # 写入goodslist.json文件
    with open(goodslist_path, 'w', encoding='utf-8') as f:
        json.dump(goods_list, f, ensure_ascii=False, indent=4)


def clear_goodslist():
    with open(goodslist_path, 'w') as file:
        file.write('')

def clear_tasklist():
    with open(tasklistpath, 'w') as file:
        file.write('')


def format_cookie_string(cookie):
    return '; '.join([f"{key}={value}" for key, value in cookie.items()])



def add_to_tasklist(goods_id,uid,game_biz,address_id,device_id,cookie,time,name):
    """
    将任务添加到任务清单中
    """
    if game_biz=="hk4e":
        region="cn_gf01"
    elif game_biz=="bh3":
        region="android01"
    elif game_biz=="hkrpg":
        region="prod_gf_cn"
    else:
        region=""

    payload = {
        "app_id": 1,
        "point_sn": "myb",
        "goods_id": goods_id,
        "exchange_num": 1,
        "uid": uid,
        "region": region,
        "game_biz": game_biz,
        "address_id": address_id
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36',
        'Accept': "application/json, text/plain, */*",
        'x-rpc-device_model': "MI 6",
        'Referer': "https://webstatic.miyoushe.com/",
        'x-rpc-device_name': "Xiaomi MI 6",
        'Origin': "https://webstatic.miyoushe.com",
        'Sec-Fetch-Dest': "empty",
        'Sec-Fetch-Site': "same-site",
        'x-rpc-device_fp': "38d7eef117a46",
        'x-rpc-channel': "xiaomi",
        'Accept-Language': "zh-CN,zh-Hans;q=0.9",
        'x-rpc-app_version': "2.71.1",
        'x-rpc-client_type': "1",
        'x-rpc-verify_key': "bll8iq97cem8",
        'x-rpc-device_id': device_id,
        'Content-Type': "application/json; charset=utf-8",
        'x-rpc-sys_version': "12",
        'Sec-Fetch-Mode': "cors",
        'Cookie': cookie
    }
    time=time
    name=name
    task = {
        "name": name,
        "payload": payload,
        "headers": headers,
        "time": time
    }
    try:
        with open(tasklistpath, 'r', encoding='utf-8') as file:
            tasklist = json.load(file)
    except Exception as e:
        tasklist = []
        print(f"Failed to read tasklist.json: {str(e)}")

    # Append the new task to the tasklist
    tasklist.append(task)

    # Save the updated tasklist back to tasklist.json
    with open(tasklistpath, 'w', encoding='utf-8') as file:
        json.dump(tasklist, file, ensure_ascii=False, indent=4)

    return tasklist


def get_cookies_from_config():
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            cookies_list = config.get('cookies_list', [])
            if cookies_list:
                return cookies_list[0]  # 获取第一个cookie对象
            else:
                raise ValueError("config.json 中的 cookies_list 为空")
    except FileNotFoundError:
        raise FileNotFoundError("找不到 config.json 文件")
    except json.JSONDecodeError:
        raise ValueError("解析 config.json 文件时出错")
    except Exception as e:
        raise RuntimeError(f"读取 config.json 时发生错误: {str(e)}")
    

def get_cookiestr_from_config():
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            cookiestr = config.get('cookie', [])
            if cookiestr:
                return format_cookie_string(cookiestr)  # 获取第一个cookie对象
            else:
                raise ValueError("config.json 中的 cookiestr 为空")
    except FileNotFoundError:
        raise FileNotFoundError("找不到 config.json 文件")
    except json.JSONDecodeError:
        raise ValueError("解析 config.json 文件时出错")
    except Exception as e:
        raise RuntimeError(f"读取 config.json 时发生错误: {str(e)}")
