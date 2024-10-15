import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# conftest.py
import asyncio
import pytest_asyncio

# Apply a consistent event loop policy for Windows
if 'win' in asyncio.get_event_loop_policy().get_event_loop().__class__.__name__.lower():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
