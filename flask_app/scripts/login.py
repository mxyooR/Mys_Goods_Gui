import requests
from qrcode.main import QRCode
import time
import uuid
import re
import os
from .log import log_message


base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(base_dir)


APP_VERSION = "2.71.1"
DEVICE_NAME = "Xiaomi MI 6"
DEVICE_MODEL = "MI 6"
SALT_6X = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
device_id = uuid.uuid4().hex

HEADERS_QRCODE_API = {
    "x-rpc-app_version": APP_VERSION,
    "DS": None,
    "x-rpc-aigis": "",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-rpc-game_biz": "bbs_cn",
    "x-rpc-sys_version": "12",
    "x-rpc-device_id": device_id,
    "x-rpc-device_name": DEVICE_NAME,
    "x-rpc-device_model": DEVICE_MODEL,
    "x-rpc-app_id": "bll8iq97cem8",
    "x-rpc-client_type": "4",
    "User-Agent": "okhttp/4.9.3",
}








def get_qr_code():
    url = "https://passport-api.miyoushe.com/account/ma-cn-passport/web/createQRLogin"
    
    response = requests.post(url, headers=HEADERS_QRCODE_API)
    print(response.text)
    data = response.json()
    print(data)
    qr_code_url = data["data"]["url"]
    ticket = data["data"]["ticket"] 
    print(f"QR Code URL: {qr_code_url}")
    print(f"Ticket: {ticket}")
    
    return qr_code_url, ticket

def show_qrcode(qr_url: str):
    """
    说明:
        显示二维码
    参数:
        :param qr_url: 二维码URL
    """
    qr = QRCode()
    qr.add_data(qr_url)
    image = qr.make_image(fill_color="black", back_color="white")
    image.save(parent_dir+"/static"+"/code.png")

def check_login_status(ticket):
    url = 'https://passport-api.miyoushe.com/account/ma-cn-passport/web/queryQRLoginStatus'
    data = {
        "ticket": ticket
    }
    
    while True:
        response = requests.post(url, json=data, headers=HEADERS_QRCODE_API)
        res = response.json()

        print(res)

        if res['retcode'] == 0:
            if res['data']['status'] == "Created":
                print("QR code scanned. Waiting for confirmation...")
            elif res['data']['status'] == "Confirmed":
                headers_dict = dict(response.headers)
                print(f"Login successful! Headers: {headers_dict}")
                return headers_dict
        else:
            print(f"Failed to check login status: {res['message']}")
            return None
            
        
        time.sleep(2)

def ReturnTotalCookie(ticket):
    
    print("Scan the QR code to log in...")
    cookie_dict={}
    cookie_headers=check_login_status(ticket)
    set_cookie = cookie_headers.get('Set-Cookie', '')
    log_message(f"成功获取cookie: {set_cookie}")
    cookie_names = ['account_id', 'ltoken', 'ltuid', 'cookie_token', 'account_mid_v2']
    # 遍历cookie名称并提取值
    for name in cookie_names:
        match = re.search(rf'{name}=([^;]+)', set_cookie)
        if match:
            cookie_dict[name] = match.group(1)
    
    print(cookie_dict)
    return cookie_dict,device_id



