# global_vars.py
import os

device_id = ""
cookie_dict={"cookies_list":{},"device_id":""}
cookie_str=""
game_biz=""
base_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(base_dir)
goodslist_path = os.path.join(base_dir, 'goodslist.json')
config_path = os.path.join(base_dir, 'config.json')
tasklistpath = os.path.join(base_dir, 'tasklist.json')