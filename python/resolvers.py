import os
import sys
import json
import uuid
import schema
import logging
from shared.kinddbsvc.KindDBSvc import KindDBSvc
from settings import KINDDB_SERVICE_URL

kindDB = KindDBSvc(tenantId=0, svcUrl=KINDDB_SERVICE_URL)
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Resolvers


def info():
    return schema.Info(
        id="7560bd6b-6a7f-45f9-97e5-38ee65982ae5",
        name="Maana Python Template",
        description="This is a python template for using MaanaQ."
    )


async def all_employees():
    employee_res = await kindDB.getAllInstancesByName(kindName="Employee")
    base = employee_res.get("allInstances")
    employees = []
    if base is not None:
        records = base.get("records")
        for r in records:
            employees.append(schema.Employee(id=r[0].get("ID"), name=r[1].get("STRING")))
    return employees


async def add_employee(employee):
    new_employee = schema.Employee(id=employee.get("id", str(uuid.uuid4())), name=employee.get("name"))
    await kindDB.addInstanceByKindName(
        "Employee",
        {
            "id": new_employee.id,
            "name": new_employee.name
        }
    )

    return new_employee


# Handlers


async def handle(event):

    parsed_event = json.loads(event)

    if "linkAdded" in parsed_event.keys():
        return await handle_file(parsed_event)


async def handle_file(blob):

    link_added = blob["linkAdded"]
    link_id = link_added["id"]

    link = await kindDB.getLink(link_id)
    logger.debug("Got link! " + json.dumps(link))

    return None
