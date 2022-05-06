import asyncio
from loguru import logger

from aiogram import Bot

from utils.config import get_config
from app.rabbit_processor import RabbitProcessor

bot = Bot(token=get_config().telegram.tg_token)


if __name__ == '__main__':
    logger.info('Start up...')

    event_loop = asyncio.new_event_loop()
    config = get_config()
    rabbit_processor = RabbitProcessor(event_loop, config, bot.send_message)

    try:
        event_loop.create_task(rabbit_processor.setup_connection())
        event_loop.run_forever()
    finally:
        event_loop.run_until_complete(rabbit_processor.close_connection())
        event_loop.close()
        logger.info('Shutting down...')
