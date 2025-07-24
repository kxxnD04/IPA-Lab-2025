import paramiko
import time

devices = {
    "S0": "172.31.4.2",
    "R0": "172.31.4.1",
}

private_key = paramiko.RSAKey.from_private_key_file("C:/Users/LAB306_XX/.ssh/id_rsa")

# กำหนด MAC, KEX, Host Key algorithms แบบ legacy
paramiko.transport._preferred_kex = ("diffie-hellman-group14-sha1",)
paramiko.transport._preferred_macs = ("hmac-sha1", "hmac-sha1-96")
paramiko.transport._preferred_keys = ("ssh-rsa",)

def backup_running_config(hostname, device_name, username="admin"):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False,
            timeout=10
        )

        # ใช้ shell interactive เพื่อรับ config เต็ม
        remote_conn = client.invoke_shell()
        time.sleep(1)
        remote_conn.send("terminal length 0\n")  # ปิด pagination
        time.sleep(0.5)
        remote_conn.send("show running-config\n")
        time.sleep(2)

        output = remote_conn.recv(65535).decode('utf-8')

        # เขียนไฟล์แยกตามชื่ออุปกรณ์
        file_path = f"./{device_name}_running_config.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"[+] Saved running config for {device_name} -> {file_path}")

    except Exception as e:
        print(f"[!] Failed to backup {device_name} ({hostname}): {e}")
    finally:
        client.close()

def ssh_connect(hostname, username='admin'):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=hostname,
            username=username,
            pkey=private_key,
            look_for_keys=False,
            allow_agent=False,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command("show version")
        print(f"\n=== {hostname} ===")
        print(stdout.read().decode())

    except Exception as e:
        print(f"[!] Failed to connect to {hostname}: {e}")
    finally:
        client.close()


# for name, ip in devices.items():
#     ssh_connect(ip)
backup_running_config(devices["R0"], "R0")
