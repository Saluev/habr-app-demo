import asyncio
import logging
import sys

from backend.wiring import Wiring

logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', stream=sys.stderr, level=logging.DEBUG)

loop = asyncio.get_event_loop()

wiring = Wiring()
loop.run_until_complete(wiring.init_async(loop))
loop.run_until_complete(wiring.game_server.serve_games())
