import sys
from urllib.parse import urlparse
import logging

log = logging.getLogger("AutoMihoyoBBS")

def get_new_session(**kwargs):
    try:
        # 优先使用httpx，在httpx无法使用的环境下使用requests
        import httpx

        http_client = httpx.Client(timeout=30, transport=httpx.HTTPTransport(retries=10), follow_redirects=True,
                                   **kwargs)
        # 当openssl版本小于1.0.2的时候直接进行一个空请求让httpx报错
        import tools

        if tools.get_openssl_version() < 102:
            httpx.get()
    except (TypeError, ModuleNotFoundError) as e:
        import requests
        from requests.adapters import HTTPAdapter

        http_client = requests.Session()
        http_client.mount('http://', HTTPAdapter(max_retries=10))
        http_client.mount('https://', HTTPAdapter(max_retries=10))
    return http_client


def is_module_imported(module_name):
    return module_name in sys.modules


def normalize_proxy_url(proxy_url):
    """
    规范化代理URL格式
    """
    if not proxy_url:
        return None
    
    # 去除空格
    proxy_url = proxy_url.strip()
    
    # 如果已经包含协议，直接返回
    if proxy_url.startswith(('http://', 'https://', 'socks5://', 'socks5h://')):
        return proxy_url
    
    # 默认添加 http://
    return f'http://{proxy_url}'


def get_new_session_use_proxy(http_proxy: str):
    """
    创建带代理的 session
    :param http_proxy: 代理地址，例如 http://127.0.0.1:7890 或 127.0.0.1:7890
    """
    # 规范化代理URL
    proxy_url = normalize_proxy_url(http_proxy)
    
    if not proxy_url:
        log.debug("未配置代理，使用直连")
        return get_new_session()
    
    log.debug(f"使用代理: {proxy_url}")
    
    # 测试代理是否可用（可选）
    try:
        test_session = get_new_session()
        test_session.proxies = {"http": proxy_url, "https": proxy_url}
        # 取消注释下面的代码来测试代理
        # test_response = test_session.get("http://httpbin.org/ip", timeout=5)
        # log.debug(f"代理测试成功，出口IP: {test_response.json().get('origin')}")
    except Exception as e:
        log.warning(f"代理测试失败: {e}")
    
    if is_module_imported("httpx"):
        # httpx 版本处理
        try:
            # 尝试新版本的 proxy 参数
            return get_new_session(proxy=proxy_url)
        except TypeError:
            # 回退到旧版本的 proxies 参数
            proxies = {
                "http://": proxy_url,
                "https://": proxy_url
            }
            return get_new_session(proxies=proxies)
    else:
        # requests 版本
        session = get_new_session()
        session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        return session


http = get_new_session()
