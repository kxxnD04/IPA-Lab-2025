from netmiko import ConnectHandler
import paramiko

# Device credentials
USERNAME = "admin"
PRIVATE_KEY_PATH = "C:/Users/LAB306_XX/.ssh/id_rsa"

# IP list by device name
devices = {
    "S1": "172.31.4.3",
    "R1": "172.31.4.6",
    "R2": "172.31.4.9"
}

# Base Netmiko connection params
BASE_PARAMS = {
    "device_type": "cisco_ios",
    "username": USERNAME,
    "use_keys": True,
    "key_file": PRIVATE_KEY_PATH,
    "allow_agent": False,
    "disabled_algorithms": {
        "pubkeys": ["rsa-sha2-256", "rsa-sha2-512"],
        "kex": [
            "diffie-hellman-group1-sha1",
            "diffie-hellman-group14-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512",
            "diffie-hellman-group-exchange-sha256",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
        ],
        "hostkeys": [
            "ssh-ed25519",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
        ],
    },
}

def connect(ip):
    params = BASE_PARAMS.copy()
    params["ip"] = ip
    return ConnectHandler(**params)

def configure_vlan(conn):
    print(f"[+] Configuring VLAN 101 on {conn.host}")
    conn.send_config_set([
        "vlan 101",
        "name CONTROL-DATA",
        "interface g0/1",
        "switchport access vlan 101",
        "switchport mode access",
        "interface g0/2",
        "switchport access vlan 101",
        "switchport mode access",
        "exit",
        "ip access-list standard MGMT-ONLY",
        "permit 172.31.4.0 0.0.0.255",
        "permit 10.30.6.0 0.0.0.255",
        "line vty 0 4",
        "access-class MGMT-ONLY in"
    ])

def configure_router(name, conn):
    print(f"[+] Configuring OSPF, NAT, and security on {name}")

    base_config = [
        "ip access-list standard MGMT-ONLY",
        "permit 172.31.4.0 0.0.0.255",
        "permit 10.30.6.0 0.0.0.255",
        "line vty 0 4",
        "access-class MGMT-ONLY in"
    ]

    if name == "R2":
        router_config = [
            "interface Loopback0",
            "vrf forwarding control-data",
            "ip address 10.1.2.1 255.255.255.255",
            "router ospf 1 vrf control-data",
            "network 172.31.4.32 0.0.0.15 area 0",
            "network 172.31.4.0 0.0.0.15 area 0",
            "network 10.1.2.1 0.0.0.0 area 0",
            "default-information originate",
            "exit",
            "ip access-list standard NAT-CONTROL",
            "permit 172.31.4.0 0.0.0.15",
            "exit",
            "ip nat inside source list NAT-CONTROL interface GigabitEthernet0/3 overload",
            "interface GigabitEthernet0/2",
            "ip nat inside",
            "interface GigabitEthernet0/3",
            "ip nat outside",
            "interface GigabitEthernet0/1",
            "ip nat inside"
        ]
    else:
        router_config = [
            "interface Loopback0",
            "vrf forwarding control-data",
            "ip address 10.1.1.1 255.255.255.255",
            "router ospf 1 vrf control-data",
            "network 172.31.4.16 0.0.0.15 area 0",
            "network 172.31.4.32 0.0.0.15 area 0",
            "network 10.1.1.1 0.0.0.0 area 0"
        ]

    full_config = base_config + router_config
    conn.send_config_set(full_config)

# Main loop
for name, ip in devices.items():
    print(f"[⏳] Connecting to {ip} ({name})...")
    conn = connect(ip)
    conn.enable()

    if name == "S1":
        configure_vlan(conn)
    else:
        configure_router(name, conn)

    conn.save_config()
    conn.disconnect()
    print(f"[✔] Configuration done for {name}\n")

print("[🏁] All configurations completed.")
