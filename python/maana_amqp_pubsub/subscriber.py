from .connection_factory import AMQPConnectionFactory
from .configuration import QueueConfig
import pika
import sys
import json
import asyncio


class AMQPSubscriber:

    def __init__(self, connection_factory):
        self.connection_factory = connection_factory

    async def subscribe(self, queue_config, action, num):
        connection = self.connection_factory.create()
        channel = connection.channel(channel_number=num)
        self.setup_channel(channel, queue_config)
        asyncio.ensure_future(self.subscribe_to_channel(channel, queue_config, action))
        return channel

    async def subscribe_to_channel(self, channel, queue_config, action):
        def callback(ch, method, properties, body):
            print(" [x] %r:%r" % (method.routing_key, body))
            try:
                action(body)
                ch.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
                return body
            except:
                ch.basic_nack(delivery_tag=method.delivery_tag, multiple=False)
                return None

        back = channel.basic_consume(callback, queue=queue_config.subscribe_queue)
        await channel.start_consuming()
        channel.stop_consuming()
        return back

    def setup_channel(self, channel, queue_config):
        try:
            channel.exchange_declare(queue_config.publish_exchange, "fanout", durable=True)
            result = channel.queue_declare(queue_config.subscribe_queue)
            out = channel.queue_bind(result.method.queue, queue_config.publish_exchange, "")
            print(out)
            return out
        except Exception as e:
            print(e)
            sys.exit(-1)
