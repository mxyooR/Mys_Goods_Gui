# 开发文档

### 兑换逻辑
```mermaid
graph TD
    A[exchange] --> B[从tasklist里面获取payload和headers]
    B -->D[获取任务异步次数`count`并封装为tasks]
    D -->C{获取 NTP 时间}
    C -->|Success| G[等待到兑换时间]
    C -->|Failure| E[Retry NTP Time]
    E --> C
    G --> H{如果delay小于60秒}
    H -->|Yes| K[异步任务开始post 
                可能会Too many requests]
    H -->|No| J[等待 30s]
    K --> L[记录结果]
    L --> M[完成任务]
    J --> C
    M --> N[结束]

```
### 兑换所需cookie：
| 字段名        | 说明   |
|--------------|--------|
| account id   | 必填   |
| cookie token | 必填   |
| ltoken       | 必填   |
| ltuid        | 必填   |
| login_ticket | 可选   |
| aliyungf_tc  | 可选   |

### 登陆方式
- 第一种手动登录，直接从用户输入的信息里面获取所需字段，代码在`app.py`和`tools.py`里面
- 第二种扫码登陆，接口参考：`https://github.com/UIGF-org/mihoyo-api-collect/blob/main/hoyolab/login/qrcode_hoyolab.md`

### 用户信息
保存在`flask_app/config.json`内，内容格式：
```json
{
    "cookies_list": {
        "ltoken": "",
        "ltuid": "",
        "account_id": "",
        "cookie_token": "",
        "account_mid_v2": ""
    },
    "device_id": ""
}
```