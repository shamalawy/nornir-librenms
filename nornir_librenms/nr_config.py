import os
from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_librenms.librenms_inventory import LibreInventory

def init_nornir(workers: int = 50, username: str=None, password: str=None, url: str=None, api_key:str=None):
    """init_nornir [summary]

    :param workers: [number of parallel workers], defaults to 50
    :type workers: int, optional
    :param username: [login username for devices], defaults to None
    :type username: str, optional
    :param password: [login password for devices], defaults to None
    :type password: str, optional
    :param url: [LibreNMS API url for devices], defaults to None
    :type url: str, optional
    :param api_key: [LibreNMS API Key], defaults to None
    :type api_key: str, optional
    :return: [Nornir Instance]
    :rtype: [nr]
    """

    os.environ['NR_USERNAME'] = username
    os.environ['NR_PASSWORD'] = password
    os.environ['NR_URL'] = url
    os.environ['NR_API_KEY'] = api_key

    InventoryPluginRegister.register(
        "librenms-inventory",
        LibreInventory,
    )

    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {"num_workers": workers},
        },
        inventory={
            "plugin": "librenms-inventory"
        },
    )
    
    return nr
