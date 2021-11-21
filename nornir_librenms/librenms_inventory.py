import requests
import os


from nornir.core.inventory import (
    ConnectionOptions,
    Defaults,
    Group,
    Groups,
    Host,
    Hosts,
    Inventory,
    ParentGroups,

)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class LibreInventory(object):

    username = os.getenv('NR_USERNAME')
    password = os.getenv(key='NR_PASSWORD')
    url = os.getenv(key='NR_URL')
    api_key = os.getenv(key='NR_API_KEY')

    def __init__(self):
        self.username = os.getenv('NR_USERNAME')
        self.password = os.getenv(key='NR_PASSWORD')
        self.url = os.getenv(key='NR_URL')
        self.api_key = os.getenv(key='NR_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-type': 'text/plan'
        }

    def get_inventory_from_libre(self):
        """
        Method to retrieve inventory from LibreNMS
        :return: [dict]
        """
        response = requests.request('GET', url=self.url, headers=self.headers)
        return response.json()['devices']

    @staticmethod
    def get_platform(os: str ) -> str:
        if os in ['ios', 'iosxe']:
            return 'cisco_ios'
        elif os in ['arista_eos', 'arista-mos', 'linux']:
            return 'arista_eos'
        else:
            print(f'{os} is not a supported os')

    def load(self) -> Inventory:
        data = self.get_inventory_from_libre()
        hosts = Hosts()
        groups = Groups()

        for device in data:
            netmiko_driver = self.get_platform(device['os'])
            name = hostname = device['hostname']
            port = 22

            groups[netmiko_driver] = Group(netmiko_driver)
            groups[device['type']] = Group(device['type'])
            groups[device['hardware']] = Group(device['hardware'])
            groups[device['os']] = Group(device['os'])

            hosts[hostname] = Host(
                name=name,
                hostname=hostname,
                platform=netmiko_driver,
                groups=ParentGroups(
                    [
                        groups[netmiko_driver],
                        groups[device['type']],
                        groups[device['hardware']],
                        groups[device['os']]
                    ]
                ),
                data={
                    "type": device['type'],
                    "model": device['hardware'],
                    "version": device['version'],
                },

                connection_options={
                    "netmiko": ConnectionOptions(
                        hostname=hostname,
                        username=LibreInventory.username,
                        password=LibreInventory.password,
                        port=22,
                        platform=netmiko_driver,
                        extras={
                            "device_type": netmiko_driver,
                            "port": 22,
                        }
                    )
                }
            )
        return Inventory(hosts=hosts, groups=Groups, defaults=Defaults)

