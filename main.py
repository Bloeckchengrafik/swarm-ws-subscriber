import asyncio
from asyncio.queues import Queue
from contextlib import contextmanager
import logging
from typing import Generator
import colorlog
from websockets import serve
import json

from config import Config, load_config
from serial_controller import SerialHandler, input_loop

class UnionQueue:
    def __init__(self) -> None:
        self.queues: list[Queue] = []

    @contextmanager
    def consumer(self) -> Generator[Queue, None, None]:
        new_queue = Queue()
        self.queues.append(new_queue)
        try:
            yield new_queue
        finally:
            self.queues.remove(new_queue)

    def produce(self, data):
        for queue in self.queues:
            queue.put_nowait(data)

async def ws(union: UnionQueue, config: Config, logger):
    async def ws_handler(websocket):
        with union.consumer() as queue:
            try:
                while True:
                    elem = await queue.get()
                    await websocket.send(elem)
            except Exception as e:
                logger.error(f"Error in ws_handler: {e}")
            finally:
                await websocket.close()

    async with serve(ws_handler, config.server_host, config.server_port) as server:
        logger.info(f"Bound to {config.server_host}:{config.server_port}")
        await server.serve_forever()

async def main():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s:%(message)s'))

    logger = colorlog.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    config = load_config()
    queue = UnionQueue()

    logger.info(f"Starting ws-subscriber on {config.server_host}:{config.server_port}")
    asyncio.create_task(ws(queue, config, logger))

    ser = SerialHandler(config.serial_port, logger)
    logger.info(f"Starting serial handler on {config.serial_port}")
    ser.try_reboot()
    logger.info(f"Rebooted serial handler")

    ports = dict.values(config.subscribers)
    reversed = {value: key for key, value in config.subscribers.items()}

    for port in ports:
        await ser.send_and_wait(f"{port}.subscribe(0)")

    async def on_subscribe(port, value):
        webalias = reversed.get(port, None)
        if webalias is None:
            logger.error(f"Unknown port {port}")
            return
        queue.produce(json.dumps({"port": port, "value": value}))

    await input_loop(ser, logger, on_subscribe)

if __name__ == "__main__":
    asyncio.run(main())
