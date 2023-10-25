from pyairtable import Api
import pyairtable.api.table as ATtable

def new_client(token:str,base:str,table:str) -> ATtable:
    api = Api(token)
    base = api.base(base)
    table = base.table(table)

    return table