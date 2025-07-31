from netmiko import ConnectHandler
import re

# Device connection info
devices = {
    "R1": "172.31.4.6",
    "R2": "172.31.4.9"
}

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

# Improved regex: Match interface that is up/up and extract name + "Last input"
interface_block_pattern = re.compile(
    r"^(?P<name>\S+) is up, line protocol is up.*?(?=^\S+ is|\Z)",  # Each interface block
    re.DOTALL | re.MULTILINE
)

last_input_pattern = re.compile(
    r"Last input\s+(?P<last_input>[\w\d:]+)", re.IGNORECASE
)

def check_active_interfaces(name, ip):
    print(f"\nConnecting and Checking On {name} ({ip})...")
    params = BASE_PARAMS.copy()
    params["ip"] = ip
    conn = ConnectHandler(**params)
    conn.enable()

    output = conn.send_command("show interfaces")
    matches = interface_block_pattern.findall(output)

    if matches:
        print(f" Active interfaces on {name}:")
        for match in interface_block_pattern.finditer(output):
            intf_name = match.group("name")
            block = match.group(0)
            last_input_match = last_input_pattern.search(block)
            last_input = last_input_match.group("last_input") if last_input_match else "N/A"
            print(f" - {intf_name:<20} Uptime: {last_input}")
    else:
        print(f" No active interfaces found on {name}.")

    conn.disconnect()

# Main loop
for name, ip in devices.items():
    check_active_interfaces(name, ip)

print("\n[🏁] Done checking all routers.")
