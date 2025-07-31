import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

# === Load YAML Configuration ===
with open("config.yaml") as f:
    config = yaml.safe_load(f)
# print(config)
USERNAME = config["credentials"]["username"]
PRIVATE_KEY = config["credentials"]["private_key"]
DEVICES = config["devices"]

# === Jinja2 Environment ===
env = Environment(loader=FileSystemLoader("templates"))

# === Netmiko Base Parameters ===
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

def connect(ip):
    params = BASE_PARAMS.copy()
    params["ip"] = ip
    return ConnectHandler(**params)

def render_and_push_config(conn, template_name, context):
    template = env.get_template(template_name)
    rendered_config = template.render(context)
    commands = rendered_config.strip().splitlines()
    conn.send_config_set(commands)

# === Main Execution ===
for name, device in DEVICES.items():
    print(f"[⏳] Connecting to {device['ip']} ({name})...")
    conn = connect(device["ip"])
    conn.enable()

    if device["type"] == "switch":
        render_and_push_config(conn, "switch_config.j2", {})
    elif device["type"] == "router":
        is_r2 = (name == "R2")
        context = {
            "loopback_ip": "10.1.2.1" if is_r2 else "10.1.1.1",
            "ospf_networks": [
                "172.31.4.32 0.0.0.15",
                "172.31.4.0 0.0.0.15" if is_r2 else "172.31.4.16 0.0.0.15",
                "10.1.2.1 0.0.0.0" if is_r2 else "10.1.1.1 0.0.0.0"
            ],
            "default_originate": is_r2,
            "is_r2": is_r2
        }
        render_and_push_config(conn, "router_config.j2", context)

    conn.save_config()
    conn.disconnect()
    print(f"[✔] Configuration done for {name}\n")

print("[🏁] All configurations completed.")
