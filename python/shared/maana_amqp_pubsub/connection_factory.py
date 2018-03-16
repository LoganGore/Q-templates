from .configuration import AmqpConnectionConfig
from aio_pika import connect
import sys


class AMQPConnectionFactory:

    def __init__(self, config: AmqpConnectionConfig):
        self.connection = "amqp://{host}:{port}".format(host=config.host, port=config.port)

    async def create(self):
        try:
            connection = await connect(self.connection)
            return connection
        except Exception as e:
            print(e)
            sys.exit(-1)
