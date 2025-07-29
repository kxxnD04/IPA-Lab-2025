# import paramiko old version
# import time

# devices = {
#     "S0": "172.31.4.2",
#     "S1": "172.31.4.3",
#     "R0": "172.31.4.1",
#     "R1": "172.31.4.6",
#     "R2": "172.31.4.9"
# }

# private_key = paramiko.RSAKey.from_private_key_file("C:/Users/LAB306_XX/.ssh/id_rsa")

# # กำหนด MAC, KEX, Host Key algorithms แบบ legacy
# paramiko.transport._preferred_kex = ("diffie-hellman-group14-sha1",)
# paramiko.transport._preferred_macs = ("hmac-sha1", "hmac-sha1-96")
# paramiko.transport._preferred_keys = ("ssh-rsa",)

# def backup_running_config(hostname, device_name, username="admin"):
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
#     try:
#         client.connect(
#             hostname=hostname,
#             username=username,
#             pkey=private_key,
#             look_for_keys=False,
#             allow_agent=False,
#             timeout=10
#         )

#         # ใช้ shell interactive เพื่อรับ config เต็ม
#         remote_conn = client.invoke_shell()
#         time.sleep(1)
#         remote_conn.send("terminal length 0\n")  # ปิด pagination
#         time.sleep(0.5)
#         remote_conn.send("show running-config\n")
#         time.sleep(2)

#         output = remote_conn.recv(65535).decode('utf-8')

#         # เขียนไฟล์แยกตามชื่ออุปกรณ์
#         file_path = f"./{device_name}_running_config.txt"
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(output)

#         print(f"[+] Saved running config for {device_name} -> {file_path}")

#     except Exception as e:
#         print(f"[!] Failed to backup {device_name} ({hostname}): {e}")
#     finally:
#         client.close()

# def ssh_connect(hostname, username='admin'):
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#     try:
#         client.connect(
#             hostname=hostname,
#             username=username,
#             pkey=private_key,
#             look_for_keys=False,
#             allow_agent=False,
#             timeout=10
#         )

#         stdin, stdout, stderr = client.exec_command("show version")
#         print(f"\n=== {hostname} ===")
#         print(f"Connect to {hostname} success!!!")
#         # print(stdout.read().decode())

#     except Exception as e:
#         print(f"[!] Failed to connect to {hostname}: {e}")
#     finally:
#         client.close()


# for name, ip in devices.items():
#     ssh_connect(ip)
# # backup_running_config(devices["R0"], "R0")
import paramiko
import time
from pathlib import Path

devices = {
    "S0": "172.31.4.2",
    "S1": "172.31.4.3",
    "R0": "172.31.4.1",
    "R1": "172.31.4.6",
    "R2": "172.31.4.9"
}

username = "admin"
password = "cisco"  # หากต้องใช้รหัสในโหมด enable
key_path = Path.home() / ".ssh" / "id_rsa"
private_key = paramiko.RSAKey.from_private_key_file(str(key_path))

def backup_running_config(hostname, device_name):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
            disabled_algorithms=dict(
                pubkeys=["rsa-sha2-256", "rsa-sha2-512"],
                kex=[
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
                hostkeys=["ssh-ed25519", "ecdsa-sha2-nistp256", "ecdsa-sha2-nistp384", "ecdsa-sha2-nistp521"],
            ),
        )

        ssh = client.invoke_shell()
        time.sleep(1)
        ssh.send("terminal length 0\n")
        time.sleep(1)
        ssh.send("enable\n")
        time.sleep(1)
        ssh.send(f"{password}\n")
        time.sleep(1)
        ssh.send("show running-config\n")
        time.sleep(2)

        output = ssh.recv(65535).decode("utf-8")
        file_path = f"./{device_name}_running_config.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"[+] Saved running config for {device_name} -> {file_path}")

    except Exception as e:
        print(f"[!] Failed to backup {device_name} ({hostname}): {e}")
    finally:
        client.close()

# Optional: test connection
def test_connection(hostname):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False,
            timeout=10,
            disabled_algorithms=dict(
                pubkeys=["rsa-sha2-256", "rsa-sha2-512"],
                kex=[
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
                hostkeys=["ssh-ed25519", "ecdsa-sha2-nistp256", "ecdsa-sha2-nistp384", "ecdsa-sha2-nistp521"],
            ),
        )
        print(f"[+] Connected to {hostname}")
    except Exception as e:
        print(f"[!] Failed to connect to {hostname}: {e}")
    finally:
        client.close()

for name, ip in devices.items():
    test_connection(ip)
    backup_running_config(ip, name)
