import os
import httpx

# 公开仓库里只能看到这个默认地址，真实地址通过 CAPTCHA_ENDPOINT 环境变量覆盖
DEFAULT_ENDPOINT = os.getenv(
    "CAPTCHA_ENDPOINT",
    "http://127.0.0.1:9645/pass_nine"
)

def captcha(gt: str, challenge: str, endpoint: str = DEFAULT_ENDPOINT):
    """
    通用验证码处理函数
    参数:
        gt: 验证码的 gt 参数
        challenge: 验证码的 challenge 参数
        endpoint: API 的端点 URL，默认读环境变量 CAPTCHA_ENDPOINT，
                  如未设置则使用 http://127.0.0.1:9645/pass_nine
    返回:
        成功时返回 validate 字符串，失败时返回 None
    """
    if not endpoint:
        print("CAPTCHA_ENDPOINT not set")
        return None

    try:
        res = httpx.get(
            endpoint,
            params={'gt': gt, 'challenge': challenge, 'use_v3_model': True},
            timeout=60
        )
        data = res.json().get('data', {})
        if data.get('result') == 'success':
            return data.get('validate')
    except (httpx.RequestError, KeyError) as e:
        print(f"Error during captcha processing: {e}")
    return None

def game_captcha(gt: str, challenge: str):
    return captcha(gt, challenge)

def bbs_captcha(gt: str, challenge: str):
    return captcha(gt, challenge)

# 本地调试示例
if __name__ == "__main__":
    gt = "example_gt"
    challenge = "example_challenge"
    print("Game captcha result:", game_captcha(gt, challenge))
    print("BBS captcha result:", bbs_captcha(gt, challenge))