

import asyncio
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
log = logging.getLogger("detox_launcher")


sys.path.insert(0, '/root/detox')


async def launch_bot(bot_name, module_path):

    try:
        log.info(f"Starting {bot_name}...")

        module = __import__(f"{module_path}.run", fromlist=['main'])
        await module.main()
    except Exception as e:
        log.error(f"{bot_name} failed: {e}", exc_info=True)

        await asyncio.sleep(10)
        await launch_bot(bot_name, module_path)


async def main():

    log.info("=" * 60)
    log.info("DETOX Bot Ecosystem Launcher")
    log.info("=" * 60)


    bots = [
        ("Hub", "hub"),
        ("Trade (MEXC)", "trade"),
        ("Escort (Violet)", "escort"),
        ("Draw", "draw"),
    ]

    tasks = []
    for bot_name, module in bots:
        task = asyncio.create_task(launch_bot(bot_name, module))
        tasks.append(task)

        await asyncio.sleep(0.5)

    log.info(f"All {len(bots)} bots started. Waiting...")

    try:

        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        log.info("Shutting down...")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        log.info("All bots stopped.")


if __name__ == "__main__":
    asyncio.run(main())
