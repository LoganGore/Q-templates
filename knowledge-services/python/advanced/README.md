## Maana Python Template

This is a template for creating a Maana Knowledge Service in Python. This requires python 3.6+

## Installation

_NOTE: REQUIRES PYTHON 3_

To install the python packages required, run this:

```
pip3 install -r requirements.txt
```

## Starting

```
python3 server.py
```

## Run unit tests

```
python3 -m pytest tests/
```

## Query Examples:

Get Service Info:

```
    	curl -XPOST http://localhost:7357/graphql -H 'Content-Type: application/json' -d '{"query": "{ info { id name description }}" }'
```

```
mutation a {
  addPerson(input:{
    id:"asdf",
    name:"fdsa"
  })
}
```
```
query b {
  person(id:"asdf") {
    id
    name
  }
}
```