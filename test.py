import asyncio
import requests
import random

GET_URL = "http://localhost/"
POST_URL = "http://localhost/add"

str = "abcdefghijklmnopqrstuvwxyz"

def fetch(name, i):
    session = requests.Session()

    # GET request
    get_res = session.get(GET_URL)

    # POST request
    post_res = session.post(POST_URL, json={"name": str[random.randint(1, len(str)-1)], "price": i})

    return (
        f"{name} [{i}] "
        f"GET: {get_res.status_code}, "
        f"POST: {post_res.status_code}"
    )

async def worker(name):
    loop = asyncio.get_running_loop()
    for i in range(10000):
        result = await loop.run_in_executor(
            None, fetch, name, i
        )
        print(result)

async def main():
    await asyncio.gather(
        worker("Worker-1"),
        worker("Worker-2")
    )

asyncio.run(main())