from netmiko import ConnectHandler
from getpass import getpass
import paramiko
# Credentials
username = "admin"
password = getpass("Enter device password: ")

# Device list
devices = {
    "S1": "172.31.4.3",
    "R1": "172.31.4.6",
    "R2": "172.31.4.9"
}


paramiko.transport._preferred_kex = ("diffie-hellman-group14-sha1",)
paramiko.transport._preferred_keys = ("ssh-rsa",)
paramiko.transport._preferred_macs = ("hmac-sha1", "hmac-sha1-96")

# Cisco device connection template
def connect(ip):
    return ConnectHandler(
        device_type="cisco_ios",
        host=ip,
        username="admin",
        use_keys=True,
        key_file="C:/Users/LAB306_XX/.ssh/id_rsa",  # หรือ path private key ของคุณ
    )

# Configure VLAN 101 on S1
def configure_vlan(switch):
    print(f"[+] Configuring VLAN 101 on {switch['host']}")
    switch.send_config_set([
        "vlan 101",
        "name CONTROL-DATA"
    ])

# Configure OSPF + default route + NAT on R1 and R2
def configure_router(name, conn):
    print(f"[+] Configuring OSPF and security on {name}")

    base_config = [
        "router ospf 1",
        "network 10.0.0.0 0.255.255.255 area 0",           # control/data plane
        "network 172.16.0.0 0.0.255.255 area 0",           # loopback
    ]

    if name == "R2":
        # default route
        base_config += [
            "ip route 0.0.0.0 0.0.0.0 g0/2",
            "router ospf 1",
            "default-information originate"
        ]

        # NAT/PAT
        nat_config = [
            "interface g0/0",
            "ip nat inside",
            "interface g0/1",
            "ip nat inside",
            "interface g0/3",
            "ip nat inside",
            "interface g0/2",
            "ip nat outside",

            "access-list 1 permit 10.0.0.0 0.255.255.255",  # control/data subnet
            "ip nat inside source list 1 interface g0/2 overload"
        ]
        base_config += nat_config

    # Restrict Telnet/SSH (ACL)
    acl = [
        "ip access-list standard MGMT-ONLY",
        "permit 172.31.4.0 0.0.0.255",  # management subnet
        "permit 10.30.6.0 0.0.0.255",   # Lab306 network
        "line vty 0 4",
        "access-class MGMT-ONLY in"
    ]

    conn.send_config_set(base_config + acl)

# Run the configuration
for name, ip in devices.items():
    conn = connect(ip)
    if name == "S1":
        configure_vlan(conn)
    elif name in ["R1", "R2"]:
        configure_router(name, conn)
    conn.save_config()
    conn.disconnect()

print("[✔] Configuration completed successfully.")
