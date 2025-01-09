import asyncio
import os
import pathlib
from robyn import Robyn, ALLOW_CORS, jsonify
from robyn.templating import JinjaTemplate

from async_request import prepare_data, operate_task, get_status

# 配置模板
current_file_path = pathlib.Path(__file__).parent.resolve()
jinja_template = JinjaTemplate(os.path.join(current_file_path, "templates"))

app = Robyn(__file__)
ALLOW_CORS(app, origins=["*"])

PASSWORD = "twelve"
task = None  # 异步任务


@app.get("/")
async def index():
    return jinja_template.render_template("protect.html")


@app.get("/index")
async def index():
    return jinja_template.render_template("index.html")


@app.post("/login")
async def login(request):
    pwd = request.json()['pwd']
    if pwd != PASSWORD:
        return jsonify({
            "status": -1,
            "message": "密码错误"
        })
    return jsonify({
        "status": 200,
        "message": "身份验证通过"
    })


@app.post("/start")
async def start(request):
    global task
    data = request.json()
    request_url = data.get("request_url")
    cookies = data.get("cookies")
    request_type = data.get("request_type")
    url_params = data.get("url_params")
    request_data = data.get("request_data")
    if not request_url:
        return jsonify({
            "status": -1,
            "message": "请先保存数据",
        })
    cookies, url_params, request_data = prepare_data(cookies, url_params, request_data)
    task = asyncio.create_task(operate_task(request_url, cookies, request_type, url_params, request_data))
    return jsonify({
        "status": 200,
        "message": "任务已开始，请打开F12控制台Console查看信息",
    })


@app.post("/stop")
async def stop():
    global task
    if not task:
        return jsonify({
            "status": -1,
            "message": "任务未开始"
        })
    task.cancel()
    try:
        await task  # 捕获取消引发的异常
    except asyncio.CancelledError:
        print("任务已停止")
    return jsonify({
        "status": 200,
        "message": "任务停止成功",
    })


# 监听状态
@app.get("/listen")
async def listen():
    current_status, first_status = get_status()
    # TODO: 判断结果
    # if 成功:
    #     await stop()
    #     返回结果
    return jsonify({
        "status": 200,
        "current_status": current_status,
        "first_status": first_status,
    })


if __name__ == "__main__":
    app.start(port=8080)
