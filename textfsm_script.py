# $env:NET_TEXTFSM = "C:\Users\LAB306_XX\Desktop\IPA\IPA-Lab-2025\venv\Lib\site-packages\ntc_templates\templates"
from netmiko import ConnectHandler
import os
from textfsm import clitable

USERNAME = "admin"
PRIVATE_KEY = "C:/Users/LAB306_XX/.ssh/id_rsa"

BASE_PARAMS = {
    "device_type": "cisco_ios",
    "username": USERNAME,
    "use_keys": True,
    "key_file": PRIVATE_KEY,
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

devices = {
    "R1": "172.31.4.6",
    "R2": "172.31.4.9",
    "S1": "172.31.4.3"
}

def connect(ip):
    params = BASE_PARAMS.copy()
    params["ip"] = ip
    return ConnectHandler(**params)

def parse_cdp(output: str):
    cli_table = clitable.CliTable(
        "index",  # <--- ใช้ index file ที่มากับ ntc-templates
        os.environ.get("NET_TEXTFSM")
    )

    attributes = {
        "Command": "show cdp neighbors",
        "Platform": "cisco_ios"
    }

    cli_table.ParseCmd(output, attributes)
    result = [dict(zip(cli_table.header, row)) for row in cli_table]
    return result

def generate_descriptions(hostname, raw_output):
    descriptions = {}
    entries = parse_cdp(raw_output)
    # print(entries)
    for entry in entries:
        local_int = entry["LOCAL_INTERFACE"]
        remote_device = entry["NEIGHBOR_NAME"].split('.')[0]
        remote_int = entry["NEIGHBOR_INTERFACE"]


        if "R" in remote_device or "S" in remote_device:
            descriptions[local_int] = f"Connect to G{remote_int} of {remote_device}"
        else:
            descriptions[local_int] = "Connect to PC"
    return descriptions

def apply_descriptions(device_name, ip):
    print(f"\nConnecting to {name} ({ip})...")
    conn = connect(ip)
    conn.enable()
    cdp_output = conn.send_command("show cdp neighbors")

    descriptions = generate_descriptions(device_name, cdp_output)
    commands = []
    for intf, desc in descriptions.items():
        commands.extend([
            f"interface {intf}",
            f"description {desc}"
        ])

    # edge case due to g0/1 of R1 did not connect to any network devices so if we run show cdp neighbors, the int g0/1 is missing and didnt configed.
    if device_name == "R1":
        commands.extend([
            f"interface g0/1",
            f"description Connect to PC"
    ])

    # edge case due to g0/3 of R2 did not connect to any network devices (its connect to NAT) so if we run show cdp neighbors, the int g0/3 is missing and didnt configed.
    if device_name == "R2":
        commands.extend([
            f"interface g0/3",
            f"description Connect to WAN"
    ])
        
    # edge case due to g0/2 of S1 did not connect to any network devices (its connect directly to pc) so if we run show cdp neighbors, the int g0/2 is missing and didnt configed.
    if device_name == "S1":
        commands.extend([
            f"interface g0/2",
            f"description Connect to PC"
    ])

    conn.send_config_set(commands)
    conn.save_config()
    conn.disconnect()
    print(f"Config Interface Description on {device_name} Success!")

# Main loop
for name, ip in devices.items():
    apply_descriptions(name, ip)

print("\n[🏁] Done config description all routers.")
