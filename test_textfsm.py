import re
from netmiko import ConnectHandler

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

def extract_description(output, interface):
    pattern = rf"^{interface}\s+\S+\s+\S+(?:\s+(?P<desc>.*))?$"
    match = re.search(pattern, output, re.MULTILINE)
    return match.group("desc").strip() if match and match.group("desc") else None


# test R1
def test_r1_descriptions():
    conn = connect(devices["R1"])
    output = conn.send_command("show interfaces description")
    conn.disconnect()

    assert extract_description(output, "Gi0/1") == "Connect to PC"
    assert extract_description(output, "Gi0/2") == "Connect to G0/1 of R2"

# test R2
def test_r2_descriptions():
    conn = connect(devices["R2"])
    output = conn.send_command("show interfaces description")
    conn.disconnect()

    assert extract_description(output, "Gi0/1") == "Connect to G0/2 of R1"
    assert extract_description(output, "Gi0/2") == "Connect to G0/1 of S1"
    assert extract_description(output, "Gi0/3") == "Connect to WAN"

# test S1
def test_s1_descriptions():
    conn = connect(devices["S1"])
    output = conn.send_command("show interfaces description")
    conn.disconnect()

    assert extract_description(output, "Gi0/1") == "Connect to G0/2 of R2"
    assert extract_description(output, "Gi0/2") == "Connect to PC"