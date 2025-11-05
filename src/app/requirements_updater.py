import asyncio
import os
import sys


async def update_requirements():
    if not await asyncio.to_thread(os.path.exists, "requirements.txt"):
        return

    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"
    )
    await process.wait()


    restart_process = await asyncio.create_subprocess_shell(
        "docker compose down && docker compose up --build -d"
    )
    await restart_process.wait()


async def requirements_updater():
    while True:
        await asyncio.sleep(3 * 24 * 60 * 60)
        await update_requirements()

