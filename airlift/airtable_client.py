from pyairtable import Api
import pyairtable.api.table as ATtable
import logging

logger = logging.getLogger(__name__)

def new_client(token:str,base:str,table:str) -> ATtable:
    api = Api(token)
    base = api.base(base)
    table = base.table(table)
    logger.debug("Client created!")
    return table