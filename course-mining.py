import json

import aiohttp
import asyncio

URL = "https://1.tongji.edu.cn/api/arrangementservice/manualArrange/page?profile"
output_file = "all-courses.json"
cookies = {
    "sessionid": "32057173e0b44c04984059b68d91f5af"
}
data = {
    "condition": {
        # "trainingLevel": "",
        # "campus": "",
        "calendar": 119,
        # "college": "",
        # "course": "",
        # "ids": [],
        # "isChineseTeaching": None
    },
    "pageNum_": None,
    "pageSize_": 20
}

count = 0
lock = asyncio.Lock()


async def mine(session, pageNum_):
    global count
    data["pageNum_"] = pageNum_
    async with session.post(URL, json=data, cookies=cookies) as response:
        response = await response.json()
        courses = response.get("data").get("list")
        for course in courses:
            with open(output_file, "a+", encoding="utf-8") as file:
                json.dump(course, file, ensure_ascii=False, indent=4)
                file.write(",\n")
                async with lock:
                    count += 1


async def main():
    with open(output_file, "a+", encoding="utf-8") as file:
        file.write("[\n")
    async with aiohttp.ClientSession() as session:
        tasks = [mine(session, x) for x in range(1, 202)]
        await asyncio.gather(*tasks)
    with open(output_file, "a+", encoding="utf-8") as file:
        file.write("\n]")
    print(f"共爬取：{count}个课程")


if __name__ == "__main__":
    # asyncio.run(main())
    pass
