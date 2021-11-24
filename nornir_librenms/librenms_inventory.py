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


class PlatformNotSupported(Exception):
    """ """


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
            return 'cisco', 'ios', 'cisco_ios'

        elif os in ['nxos']:
            return 'cisco', 'nxos', 'cisco_nxos'

        elif os in ['iosxr']:
            return 'cisco', 'iosxr', 'cisco_iosxr'

        elif os in ['asa']:
            return 'cisco', 'asa', 'cisco_asa'

        elif os in ['arista_os', 'arista_mos']:
            return 'arista', 'eos', 'arista_mos'

        elif os in ['aruba']:
            return 'aruba', 'aruba_os', 'aruba_os'

        elif os in ['panos']:
            return 'palo_alto', 'paloalto_panos', 'paloalto_panos'

        elif os in ['procurve']:
            return 'hp', 'hp_procurve', 'hp_procurve'

        elif os in ['comware']:
            return 'hp', 'hp_comware', 'hp_comware'

        elif os in ['f5']:
            return 'f5', 'f5_tmsh', 'f5_tmsh'

        elif os in ['dnos']:
            return 'dell', 'dell_dnos', 'dell_dnos'

        elif os in ['linux']:
            return 'linux', 'linux', 'linux'
        else:
            print(f'{os} is not a supported os')

    def load(self) -> Inventory:
        data = self.get_inventory_from_libre()
        hosts = Hosts()
        groups = Groups()

        for device in data:
            try:
                vendor, os_type, netmiko_driver = self.get_platform(device['os'])
            except Exception as e:
                continue

            name = hostname = device['hostname']
            port = 22

            groups[netmiko_driver] = Group(netmiko_driver)
            groups[device['type']] = Group(device['type'])
            groups[device['hardware']] = Group(device['hardware'])
            groups[device['os']] = Group(device['os'])
            groups[vendor] = Group(vendor)

            hosts[hostname] = Host(
                name=name,
                hostname=hostname,
                platform=os_type,
                groups=ParentGroups(
                    [
                        groups[netmiko_driver],
                        groups[device['type']],
                        groups[device['hardware']],
                        groups[device['os']],
                        groups[vendor],
                    ]
                ),
                data={
                    "type": device['type'],
                    "model": device['hardware'],
                    "vendor": vendor,
                    "version": device['version'],
                    "location": device['location'],
                    "version": device['version'],
                    "serial": device['serial'],
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
                            "port": port,
                            "global_delay_factor": 4
                        }
                    )
                }
            )
        return Inventory(hosts=hosts, groups=Groups, defaults=Defaults)

