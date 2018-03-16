import os
import uuid
import json
import schema
import asyncio
from shared.kinddbsvc.KindDBSvc import KindDBSvc

kindDB = KindDBSvc(0, os.getenv('KINDDB_SERVICE_URL', 'http://localhost:8008/graphql'))


def info():
    return schema.Info(
        id="7560bd6b-6a7f-45f9-97e5-38ee65982ae5",
        name="Maana Python Template",
        description="This is a python template for using MaanaQ."
    )


async def all_employees():
    employee_res = await kindDB.getAllInstances(kindName="Employee")
    base = employee_res.get("allInstances")
    employees = []
    if base is not None:
        records = base.get["records"]
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
    # This is where you'd make more complicated logic to handle events
    await asyncio.sleep(1.)
    return blob