# nornir-librenms
LibreNMS inventory plugin for Nornir network automation

## Usage

The library will take care of a few things for you
1) Populate the inventory
2) Append some data to the device instance like version, model and device type ( as detected by librenms )
3) generate basic netmiko connection options in assumption that it's using ssh


#### Import the package
```
>>>from nornir_librenms.nr_config import init_nornir
```
#### Instantiate a nornir instance using librenms inventory and devices login username and password
```
>>>nr = init_nornir(
    username='admin',
    password='mypassword',
    url='http://mylibrenms/api/v0/devices/',
    api_key='abcedef123456'
)
```
#### The nr instance should now contain all the devices in librenms
```
>>>nr.inventory.hosts
{'192.168.0.20': Host: 192.168.0.20, '192.168.0.22': Host: 192.168.0.22, '192.168.0.24': Host: 192.168.0.24}
```
#### It will also include metadata and populate netmiko extra configurations by default for your convenience
```
>>> nr.inventory.hosts['192.168.0.20'].data
{'type': 'network', 'model': 'IOSv', 'version': '15.5(3)M'}

>>> nr.inventory.hosts['192.168.0.20'].connection_options['netmiko'].extras
{'device_type': 'cisco_ios', 'port': 22}
```
and you're good to go!
