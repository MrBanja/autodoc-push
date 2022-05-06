import asyncio
from typing import Optional

import aio_pika
import ujson
from loguru import logger
from pydantic import ValidationError

from app.models import BasicPush
from utils.config import AppConfig

log = logger


class RabbitProcessor:

    def __init__(self, loop: asyncio.AbstractEventLoop, config: AppConfig, sender_function: callable):
        self.config = config

        self.log = log
        self._sender_function = sender_function

        self.__loop = loop
        self.__connection: Optional[aio_pika.Connection] = None
        self.__channel: Optional[aio_pika.Channel] = None

    async def setup_connection(self):
        connection: aio_pika.connection.AbstractConnection = await aio_pika.connect_robust(
            host=self.config.rmq.host,
            virtualhost=self.config.rmq.vhost,
            login=self.config.rmq.username,
            password=self.config.rmq.password.get_secret_value(),
            loop=self.__loop,
        )

        channel: aio_pika.channel.AbstractChannel = await connection.channel()

        self.log.info('Establish Rabbit connection')
        self.__connection = connection
        self.__channel = channel

        queue: aio_pika.queue.AbstractQueue = await channel.declare_queue('push', durable=True)
        await queue.consume(self.process_message)

    async def close_connection(self):
        if self.__connection:
            await self.__connection.close()
            self.log.info('Rabbit connection closed')

    async def process_message(self, message: aio_pika.message.AbstractIncomingMessage):
        async with message.process():
            try:
                message_body = ujson.loads(message.body)
            except ValueError:
                self.log.error(f'Can not parse message body. MESSAGE: [{message.body}]')
                return
            try:
                push = BasicPush.parse_obj(message_body)
            except ValidationError as e:
                self.log.error(f'Can not Validate: [{e.errors()}]')
                return

            await self.process_push(push)

    async def process_push(self, push: BasicPush):
        await self._sender_function(push.telegram_user_id, push.message)
