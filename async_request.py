import asyncio
import json

import aiohttp

# 全局变量
count = 0  # 请求次数
current_status = ""  # 当前状态
lock = asyncio.Lock()  # 创建一个锁


def prepare_data(cookies, url_params, request_data):
    if cookies:
        cookies = json.loads(cookies)
    if url_params:
        url_params = json.loads(url_params)
    if request_data:
        request_data = json.loads(request_data)
    return [cookies, url_params, request_data]


# 必须用函数才能在app.py正确获取到current_status实时更新的值
def get_current_status():
    return current_status


# 发起一次请求
async def single_request(session, request_url, url_params=None, request_data=None, request_type="GET"):
    global count, current_status
    try:
        # 将请求类型转换为小写，确保一致性
        request_type = request_type.lower()
        # 使用 getattr 动态调用方法，如 session.get、session.post 等
        if hasattr(session, request_type):
            async with getattr(session, request_type)(url=request_url, params=url_params,
                                                      json=request_data) as response:
                # 根据 Content-Type 动态处理响应
                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    res = await response.json()
                elif 'text/' in content_type:
                    res = await response.text()
                else:
                    res = await response.read()  # 针对未知或二进制内容

                # 使用锁保护对 count 的修改
                async with lock:
                    count += 1
                # 更新当前状态
                current_status = {
                    "message": f"已发送请求：{count}次",
                    "response": res,
                }
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
    except Exception as e:
        current_status = {
            "message": f"已发送请求：{count}次",
            "response": f"Error: {e}",
        }


# 异步发起多次请求
async def operate_task(request_url, cookies, request_type, url_params, request_data):
    global count
    count = 0
    async with aiohttp.ClientSession(cookies=cookies, connector=aiohttp.TCPConnector(ssl=False)) as session:
        while True:
            tasks = [asyncio.create_task(single_request(session, request_url, url_params, request_data, request_type))
                     for _ in range(300)]
            await asyncio.gather(*tasks)  # 等待所有任务完成
