import graphql
from graphql import build_ast_schema
from graphql.language.parser import parse
from aioify import aioify
import re
import logging
import pprint
import pickle
import hashlib
import os
import time
import subprocess


def empty_cache(persistent=False):

    cache_folder = "cache"

    if persistent:
        cache_folder = '/service_source/cache'

    delete_process = subprocess.Popen('rm ' + cache_folder + "/*", shell=True)
    delete_process.wait()

# TODO: Have this use memory for performance and use textit to dump to disk
# https://docs.python.org/3/library/shelve.html <- potential option?
def cache_query(ttl=3600, persistent=False):
    '''Decorator used for caching intensive queries'''

    def decorator(original_func):

        def new_func(*args, **kwargs):
            # Our key is made from the funciton name and the keyword arguments - i.e value and info are ignored
            cache_key = hashlib.md5(original_func.__name__.encode(
                'utf-8') + pickle.dumps(kwargs)).hexdigest()

            # This is in the working /app folder so will be wiped when the service is restarted/watch mode
            cache_folder = "cache"

            # This is stored in volume mount for the source code, so it stays when you modify code
            # This is useful for development and stuff that we know won't change
            if persistent:
                cache_folder = '/service_source/cache'

            tmp_file = cache_folder + f'/{original_func.__name__}_' + cache_key

            cached_result = False

            # load the cache from disk
            try:
                mtime = os.path.getmtime(tmp_file)
                time_now = time.time()
                age = time_now - mtime

                # If it's younger than our ttl, use it
                if age < ttl or persistent is True:
                    cached_result = pickle.load(open(tmp_file, 'rb'))
                    # print(original_func.__name__ + " cache hit.", cache_key)
            except:
                pass

            if cached_result is False:
                # Let us know it's a miss
                print(original_func.__name__ + " cache miss.", cache_key)

                # run it
                cached_result = original_func(*args, **kwargs)

                # make sure the directory exists
                try:
                    os.mkdir(cache_folder, mode=0o755)
                except:
                    pass

                # store it
                # TODO: Move to cPickle for better performance?
                pickle.dump(cached_result, open(tmp_file, 'wb'))

            return cached_result

        return new_func

    return decorator

# Original before mods: https://gist.github.com/jasonphillips/d80642fc33d98cb34bad131adfcf6ed8
# accepts schema_definition (string) and resolvers (object) in style of graphql-tools
# returns a schema ready for execution


def build_executable_schema(schema_definition, resolvers, scalars):
    ast = graphql.parse(schema_definition)
    schema = graphql.build_ast_schema(ast)

    #aioify our resolver functions
    def aioify_resolvers(node):

        if callable(node):
            #our leafs
            return aioify(obj=node)

        for key,value in node.items():                
            node[key] = aioify_resolvers(value)

        return node  

    #recursively wrap our functions to make them async
    resolvers = aioify_resolvers(resolvers)

    for scalar in scalars:
        type = schema.get_type(scalar)

        # Ignore scalars we aren't using in this schema
        if not type:
            continue

        type.description = scalars[scalar]['description']
        type.serialize = scalars[scalar]['serialize']
        type.parse_literal = scalars[scalar]['parse_literal']
        type.parse_value = scalars[scalar]['parse_value']

    for typeName in resolvers:
        fieldType = schema.get_type(typeName)

        for fieldName in resolvers[typeName]:
            if fieldType is graphql.GraphQLScalarType:
                fieldType.fields[fieldName].resolver = resolvers[typeName][fieldName]
                continue

            field = fieldType.fields[fieldName]
            field.resolve = resolvers[typeName][fieldName]

        if not fieldType or not fieldType.fields:
            continue

        for remaining in fieldType.fields:
            if not fieldType.fields[remaining].resolve:
                fieldType.fields[remaining].resolve = \
                    lambda value, info, _r=remaining, **args: value[_r] if _r in value else None

    return schema


def schema_prioritise(base_schema, priority_schema):
    '''Parse base & priority strings into GraphQL Schemas'''
    ast_base = graphql.parse(base_schema)
    schema_base = graphql.build_ast_schema(ast_base)
    ast_priority = graphql.parse(priority_schema)

    '''Update the base schema with keys from the new schema'''
    schema_priority = graphql.build_ast_schema(ast_priority)
    schema_base.type_map.update(schema_priority.type_map)

    '''Generate new schema string from updated typemap'''
    new_schema_string = generate_schema_from_typemap(schema_base.type_map)

    return new_schema_string

# TODO: Ashish: Please refactor this and portal_to_model instead of copy/paste
def generate_schema_from_typemap(type_map):
    native_types = ['Mutation', '__Schema', '__Type', '__Field',
                    '__InputValue', '__EnumValue', '__Directive', 'Query']

    maana_types = ['FieldValue', 'FieldValueInput',
                   'InstanceSet', 'InstanceSetInput', 'InfoInput']

    scalars = list({k: v for (k, v) in type_map.items() if isinstance(
        v, graphql.type.definition.GraphQLScalarType)}.keys())

    new_schema = ""
    for type in type_map:

        '''Skip Types that are autogenerated by the platform'''
        if type in maana_types or type in native_types:
            continue

        '''Transform only the Types. Ignore the autogenerated InputTypes'''
        if isinstance(type_map[type], graphql.type.definition.GraphQLObjectType):

            new_type = "type {} {{\n".format(type)
            new_input_type = "input {}Input {{\n".format(type)

            for field in type_map[type].fields:

                '''field, fieldType are the name and type of the current field'''
                field_type = str(
                    type_map[type].fields[field].type)

                # Is this field required?
                required = "!" if "!" in field_type else ""
                field_type = field_type.replace("!", "")
                field_type = field_type[:-
                                        1] if (field_type.endswith("]")) else field_type

                '''Format new input type '''
                new_input_field = "{}: {}Input{}".format(
                    field, field_type, required) if field_type not in scalars else "{}: {}{}".format(field, field_type, required)

                # Add our closing square bracket back if needed
                new_input_field = new_input_field + \
                    "]" if ('[' in field_type) else new_input_field

                '''Format new type'''
                new_type = new_type + \
                    "\t{}: {}".format(field, str(
                        type_map[type].fields[field].type)) + "\n"
                new_input_type = new_input_type + "\t" + new_input_field + "\n"

            '''Append newly created types'''
            new_input_type = new_input_type + "}\n"
            new_type = new_type + "}\n"
            new_schema = new_schema + new_type + "\n" + new_input_type + "\n"

    new_schema += "\n"

        # Add our scalars in
    for scalar in scalars:
        new_schema = new_schema + "scalar " + scalar + "\n"

    # Remove any additional new lines from the end
    new_schema = new_schema.rstrip("\n")

    return new_schema

def portal_to_model(filepath):
    '''
        Takes a schema from the Maana Q Portal, creates input types with hard references to nested input types
        (as opposed to IDs) and removes all boilerplate mutations and queries
    '''

    # Our starting point
    new_schema = ""
    with open(filepath, "r") as f:

        # read the contents of the file and build the ast
        model_schema_string = f.read()
        model_schema = build_ast_schema(parse(model_schema_string))

        # We use these lookups later to ignore certain types
        native_types = ['Mutation', '__Schema', '__Type', '__Field',
                        '__InputValue', '__EnumValue', '__Directive', 'Query']

        maana_types = ['FieldValue', 'FieldValueInput',
                       'InstanceSet', 'InstanceSetInput', 'InfoInput']

        '''Scalar types wont have an "Input" appended before it, so we need to filter them out'''
        scalars = list({k: v for (k, v) in model_schema.type_map.items(
        ) if isinstance(v, graphql.type.definition.GraphQLScalarType)}.keys())

        for type in model_schema.type_map:

            '''Skip Types that are autogenerated by the platform'''
            if type in maana_types or type in native_types:
                continue

            '''Transform only the Types. Ignore the autogenerated InputTypes'''
            if isinstance(model_schema.type_map[type], graphql.type.definition.GraphQLObjectType):

                new_type = "type {} {{\n".format(type)
                new_input_type = "input {}Input {{\n".format(type)

                for field in model_schema.type_map[type].fields:

                    '''field, fieldType are the name and type of the current field'''
                    field_type = str(
                        model_schema.type_map[type].fields[field].type)

                    # Is this field required?
                    required = "!" if "!" in field_type else ""
                    field_type = field_type.replace("!", "")
                    field_type = field_type[:-
                                            1] if (field_type.endswith("]")) else field_type

                    '''Format new input type '''
                    new_input_field = "{}: {}Input{}".format(
                        field, field_type, required) if field_type not in scalars else "{}: {}{}".format(field, field_type, required)

                    # Add our closing square bracket back if needed
                    new_input_field = new_input_field + \
                        "]" if ('[' in field_type) else new_input_field

                    '''Format new type'''
                    new_type = new_type + \
                        "\t{}: {}".format(field, str(
                            model_schema.type_map[type].fields[field].type)) + "\n"
                    new_input_type = new_input_type + "\t" + new_input_field + "\n"

                '''Append newly created types'''
                new_input_type = new_input_type + "}\n"
                new_type = new_type + "}\n"
                new_schema = new_schema + new_type + "\n" + new_input_type + "\n"

        new_schema += "\n"

        # Add our scalars in
        for scalar in scalars:
            new_schema = new_schema + "scalar " + scalar + "\n"

        # Remove any additional new lines from the end
        new_schema = new_schema.rstrip("\n")

    return new_schema


def format_resolver(args, return_type):
    '''Formats resolvers for GraphQL Query and Mutation types'''
    arg_string = "("

    for argName, argValue in args.items():
        arg_string = arg_string + " {}: {},".format(argName, argValue.type)

    '''Remove last comma'''
    arg_string = arg_string[:-1]
    arg_string = arg_string + " ): " + str(return_type) + "\n"

    return arg_string


def generate_typestring(parent_type, sub_types, args):
    '''
        return a formatted type string with all nested types in a format
        which follows the GraphQL schema definition. Ex: type Component { ... }
    '''
    prefix = "input" if parent_type.endswith("Input") else "type"

    type_string = "\n{} {} {{\n".format(prefix, parent_type)

    for sub_type in sub_types:

        if (isinstance(sub_types[sub_type], graphql.type.definition.GraphQLField) and sub_types[sub_type].args):
            new_sub_type = sub_type + " " + \
                format_resolver(sub_types[sub_type].args,
                                sub_types[sub_type].type)
        else:
            new_sub_type = "\t{}: {}\n".format(
                sub_type, sub_types[sub_type].type)
        type_string = type_string + new_sub_type

    type_string = type_string + "}\n"

    return type_string


def parse_return_types(type_map):
    '''Extract the types returned by functions in a GraphQLSchema'''
    types_in_map = set()

    '''For each field name, extract its raw type and add it to a set'''
    for field in type_map.fields:
        return_type = type_map.fields[field].type
        return_type = ''.join(ch for ch in str(return_type) if ch.isalnum())
        types_in_map.add(return_type)

    return types_in_map


def parse_arguments(type_map):
    '''Return a set containing all types used in the arguments of a GraphQLSchema'''
    types_in_map = set()

    for field in type_map.fields:

        '''Iterate through all argument types, removing non alpha chars (![])'''
        for value in type_map.fields[field].args.values():
            new_type = ''.join(ch for ch in str(value.type) if ch.isalnum())
            types_in_map.add(new_type)

    return types_in_map


def get_all_types_from_query_and_mutation(schema):
    '''Return a set of the types defined in queries and mutations inside
        a GraphQLSchema object'''

    queries = schema.type_map['Query']
    mutation = schema.type_map['Mutation']

    '''Extract the types returned in all query + mutation functions'''
    return_types = parse_return_types(
        queries).union(parse_return_types(mutation))

    '''Extract the types used in arguments in all query + mutation functions'''
    types_in_argument = parse_arguments(
        queries).union(parse_return_types(mutation))

    return return_types.union(types_in_argument).union(set(["Query", "Mutation"]))


def filter_schema(schema, filtered):
    '''
        Given an entire schema and a set of fields, generate a subschema containing
        all the fields in the set along with any nested fields and scalars
    '''

    seen = set()  # set of all types/scalars we've already encountered as we traverse
    trimmed_schema = {  # map of GraphQL type to typestring. ex: component -> type component { ... }
        'scalars': []
    }
    stack = list(filtered)

    while stack:
        '''Remove items like []! and isolate name of newest type'''
        curr_type = stack.pop()
        new_type = ''.join(ch for ch in str(curr_type) if ch.isalnum())

        if (new_type in seen):
            continue

        '''Scalars don't have subtypes so no need to process further'''
        if (isinstance(schema.type_map[new_type], graphql.GraphQLScalarType)):
            trimmed_schema['scalars'].append(new_type)
            seen.add(new_type)
            continue

        '''Generate typestring and add to map'''
        trimmed_schema[new_type] = generate_typestring(
            new_type, schema.type_map[new_type].fields, "")
        seen.add(new_type)

        '''Add all subtypes to the stack'''
        for field in schema.type_map[new_type].fields:
            nested_type = str(schema.type_map[new_type].fields[field].type)

            if (nested_type in seen or nested_type in stack):
                continue
            else:
                stack.append(nested_type)

    return generate_schema_string(trimmed_schema)


def generate_schema_string(schema_map):
    '''Return a String representation of the GraphQLSchema from a dictionary of types'''

    schema = ""

    for gql_type in schema_map:
        '''Add the Scalar or GraphQLObjectType to the schema'''
        if (gql_type == "scalars"):

            for scalar in schema_map[gql_type]:
                schema = "{}\nscalar {}".format(schema, scalar)
        else:
            schema = schema + schema_map[gql_type]

    return schema


def concat_schemas(schema_list):
    '''Given a list of schema paths return one schema string'''
    schema = ""

    for curr_schema in schema_list:

        with open(curr_schema, "r") as f:
            new_schema = f.read()
            schema = schema + "\n" + new_schema + "\n"

    return schema.strip()


def remove_unused_deps(schema):
    types_in_graphql_resolvers = get_all_types_from_query_and_mutation(schema)
    return filter_schema(schema, types_in_graphql_resolvers)
