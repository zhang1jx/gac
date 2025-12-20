import json
import os
import requests
from pypushdeer import PushDeer


CHECKIN_URL = "https://glados.one/api/user/checkin"
STATUS_URL = "https://glados.one/api/user/status"

REFERER = "https://glados.one/console/checkin"
ORIGIN = "https://glados.one"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.0.0 Safari/537.36"
)

PAYLOAD = {"token": "glados.one"}
TIMEOUT = 10


def build_headers(cookie: str) -> dict:
    return {
        "cookie": cookie,
        "referer": REFERER,
        "origin": ORIGIN,
        "user-agent": USER_AGENT,
        "content-type": "application/json;charset=UTF-8",
    }


def push_message(sckey: str, title: str, content: str):
    if not sckey:
        print("Not push")
        return
    PushDeer(pushkey=sckey).send_text(title, desp=content)


def main():
    sckey = os.environ.get("SENDKEY", "")
    cookies_env = os.environ.get("COOKIES", "")
    cookies = cookies_env.split("&") if cookies_env else []

    success = fail = repeats = 0
    context = ""

    if not cookies:
        title = "# 未找到 cookies!"
        push_message(sckey, title, context)
        return

    session = requests.Session()

    for cookie in cookies:
        email = ""
        points = 0
        message_days = "error"
        message_status = ""

        try:
            headers = build_headers(cookie)

            checkin_resp = session.post(
                CHECKIN_URL,
                headers=headers,
                data=json.dumps(PAYLOAD),
                timeout=TIMEOUT,
            )

            status_resp = session.get(
                STATUS_URL,
                headers=headers,
                timeout=TIMEOUT,
            )

            if checkin_resp.status_code == 200:
                checkin_data = checkin_resp.json()
                check_result = checkin_data.get("message", "")
                points = checkin_data.get("points", 0)

                print(check_result)

                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = f"签到成功，会员点数 + {points}"
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                # ===== 关键修复：安全解析 status 接口 =====
                status_json = status_resp.json()
                data = status_json.get("data")

                if isinstance(data, dict):
                    leftdays = int(float(data.get("leftDays", 0)))
                    email = data.get("email", "")
                    message_days = f"{leftdays} 天"
                else:
                    fail += 1
                    message_status += " / 状态获取失败"
                    message_days = "error"

            else:
                fail += 1
                message_status = "签到请求URL失败, 请检查..."

        except Exception as e:
            fail += 1
            message_status = f"异常错误: {e}"

        context += f"账号: {email}, P: {points}, 剩余: {message_days} | "

    title = f"Glados, 成功{success},失败{fail},重复{repeats}"
    print("Send Content:\n", context)

    push_message(sckey, title, context)


if __name__ == "__main__":
    main()
