import asyncio

async def fetch_data():
    print("Fetching data...")
    await asyncio.sleep(2)
    print("Data fetched!")

async def process_data():
    print("Processing data...")
    await asyncio.sleep(1)
    print("Data processed!")
