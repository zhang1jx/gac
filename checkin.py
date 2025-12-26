import os
import json
import time
import random
import requests
from pypushdeer import PushDeer

# ... (保留原有的 URL 和 HEADERS 配置) ...

def main():
    sckey = os.getenv("SENDKEY", "")
    cookies_env = os.getenv("COOKIES", "")
    cookies = [c.strip() for c in cookies_env.split("&") if c.strip()]

    if not cookies:
        push(sckey, "GLaDOS 签到", "❌ 未检测到 COOKIES")
        return

    # --- 新增：随机启动延时 ---
    # 如果在 GitHub Actions 等环境运行，建议随机等待 0-1800 秒（30分钟）
    # 这样可以避免多个用户在同一秒请求服务器，降低被封禁风险
    wait_time = random.randint(1, 600) # 这里设置为 1-600 秒，可根据需要调整
    print(f"为了模拟真实行为，脚本将随机等待 {wait_time} 秒后开始执行...")
    time.sleep(wait_time)
    # -----------------------

    session = requests.Session()
    ok = fail = repeat = 0
    lines = []

    for idx, cookie in enumerate(cookies, 1):
        # 账号间的随机延时（代码原本已有，可适当加大范围）
        if idx > 1:
            account_wait = random.uniform(5, 15) 
            print(f"账号间休息 {account_wait:.2f} 秒...")
            time.sleep(account_wait)

        headers = dict(HEADERS_BASE)
        headers["cookie"] = cookie

        # ... (后续逻辑保持不变) ...

