from shared.maana_amqp_pubsub import amqp_pubsub, configuration

pubsub = amqp_pubsub.AmqpPubSub(configuration.AmqpConnectionConfig("127.0.0.1", "5672", "MPT"))
