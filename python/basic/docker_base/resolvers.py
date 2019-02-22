import logging

logger = logging.getLogger(__name__)

resolvers = {
    'Query': {
        'test': lambda value, info, **args: "blah"
    },
    'Mutation': {
        'test': lambda value, info, **args: "blah"
    },
}
