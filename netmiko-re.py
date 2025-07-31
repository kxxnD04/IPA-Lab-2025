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

# Regex patterns
interface_block_pattern = re.compile(
    r"^(?P<name>\S+) is up, line protocol is up.*?(?=^\S+ is|\Z)",
    re.DOTALL | re.MULTILINE
)

uptime_pattern = re.compile(
    r"(?P<hostname>\S+) uptime is (?P<uptime>.+)"
)

def check_active_interfaces_and_uptime(name, ip):
    print(f"\n Connecting to {name} ({ip})...")
    params = BASE_PARAMS.copy()
    params["ip"] = ip
    conn = ConnectHandler(**params)
    conn.enable()

    # Check active interfaces from "show interfaces"
    interfaces_output = conn.send_command("show interfaces")
    matches = interface_block_pattern.findall(interfaces_output)

    if matches:
        print(f">>> Active interfaces on {name}:")
        for match in interface_block_pattern.finditer(interfaces_output):
            intf_name = match.group("name")
            print(f" - {intf_name:<20}")
    else:
        print(f" !!! No active interfaces found on {name}")

    # Check uptime from "show version"
    version_output = conn.send_command("show version")
    uptime_match = uptime_pattern.search(version_output)
    if uptime_match:
        uptime = uptime_match.group("uptime")
        print(f">>> {name} uptime: {uptime}")
    else:
        print(f"!!! Could not find uptime for {name}")

    conn.disconnect()

# === Main Execution ===
for name, ip in devices.items():
    check_active_interfaces_and_uptime(name, ip)

print("\n[🏁] All routers checked.")
