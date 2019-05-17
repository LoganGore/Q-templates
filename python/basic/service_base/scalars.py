from dateutil.parser import parse
import datetime
import sys
from six import string_types
from graphql.language.ast import BooleanValueNode, FloatValueNode, IntValueNode, StringValueNode

scalars = {
    # 'Date': {
    #     'description': "Date. Supports being passed in as a string and will try to figure out the proper formatting.",
    #     'parse_literal': lambda value: coerce_date_literal(value),
    #     'parse_value': lambda value: coerce_date(value),
    #     'serialize': lambda value: serialize_date(value)
    # },
    'Date': {
        'description': "RFC 3339 Date Scalar as used in Q. Returns a datetime object.",
        'parse_literal': lambda value: parse_datetime(value),
        'parse_value': lambda value: parse_datetime(value),
        'serialize': lambda value: serialize_datetime(value)
    },
    'DateTime': {
        'description': "RFC 3339 DateTime Scalar as used in Q. Returns a datetime object.",
        'parse_literal': lambda value: parse_datetime(value),
        'parse_value': lambda value: parse_datetime(value),
        'serialize': lambda value: serialize_datetime(value)
    }
}

'''DateTime'''

def serialize_datetime(value):
    # GraphQl String/Int/Float
    if isinstance(value, StringValueNode):
        value = value.value

    if isinstance(value, FloatValueNode):
        value = float(value.value)

    if isinstance(value, IntValueNode):
        value = int(value.value)

    # If it's a string, it's (hopefully) already in the right format
    if isinstance(value, string_types):
        return value

    # If it's a python datetime object, convert to a RFC 3339 string
    if isinstance(value, datetime.datetime):
        return value.isoformat()

    # If it's a timestamp, convert it to an RFC 3339 string
    if isinstance(value, int) or isinstance(value, float):
        return datetime.datetime.utcfromtimestamp(value).isoformat()

    return None


def parse_datetime(value):
    # GraphQl String/Int/Float
    if isinstance(value, StringValueNode):
        value = value.value

    if isinstance(value, FloatValueNode):
        value = float(value.value)

    if isinstance(value, IntValueNode):
        value = int(value.value)

    # Actual String
    if isinstance(value, string_types):
        # return datetime.datetime.fromisoformat(value)
        return parse(value)

    # Python datetime
    if isinstance(value, datetime.datetime):
        return value

    # Timestamp
    if isinstance(value, int) or isinstance(value, float):
        return datetime.datetime.utcfromtimestamp(value)

    return None


'''Date'''

# This was the original code Almir wrote, here in case I missed something.

# def coerce_date(value):
#     # type: (str) -> Optional[datetime]
#     if isinstance(value, string_types):
#         return parse(value)

#     if isinstance(value, datetime.datetime):
#         return value

#     # if isinstance(value, int):
#         # return datetime.datetime.fromtimestamp(value)

#     return None


# def serialize_date(value):
#     # type: (str) -> Optional[datetime]
#     if isinstance(value, string_types):
#         return value

#     if isinstance(value, datetime.datetime):
#         return str(value)

#     # if isinstance(value, int):
#         # return datetime.datetime.fromtimestamp(value)

#     return None


# def coerce_date_literal(ast):
#     # type: (Union[StringValue]) -> Optional[datetime]
#     if isinstance(ast, StringValue):
#         return parse(ast.value)

#     return None
