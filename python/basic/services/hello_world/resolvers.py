import logging
logger = logging.getLogger(__name__)

from graphql_tools import cache_query

# If you want to cache your query, use our built in decorator. See README for more information.
@cache_query()
def helloWorld(value, info, **args):

    #All of our parameters for the query are held in args as a dictionary
    return f"hello {args['name']}!"

resolvers = {
    'Query': {
        'info': lambda value, info, **args: "Hello World example.",
        'helloWorld': helloWorld
    },
    'Mutation': {
        'info': lambda value, info, **args: "Hello World example."
    }    
}