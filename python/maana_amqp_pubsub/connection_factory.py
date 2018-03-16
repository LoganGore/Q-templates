import pika
from .configuration import AmqpConnectionConfig


class AMQPConnectionFactory:

    def __init__(self, config: AmqpConnectionConfig):
        self.connection = "amqp://{host}:{port}".format(host=config.host, port=config.port)

    def create(self):
        return pika.BlockingConnection(pika.URLParameters(self.connection))

    def on_connection_open(self):
        print("Connected to RabbitMQ on {}".format(self.connection))
