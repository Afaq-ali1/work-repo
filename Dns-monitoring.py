#!/usr/bin/env python3

import os
import smtplib
import subprocess
import time
from datetime import datetime
from email.message import EmailMessage

DNS_SERVERS = [
    "103.125.176.8",
    "103.125.176.9",
    "103.125.176.12",
    "103.125.176.13",
    "103.125.176.14",
    "103.125.176.15",
    "103.125.176.16",
    "103.125.176.18",
    "103.125.176.19",
    "103.125.176.20"
]

QUERY = "google.com"
CHECK_INTERVAL = 60

GMAIL_USER = os.getenv("aafaq.ali.5209@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("rpse rnhg pzgd qhra")
GMAIL_TO = os.getenv("afaq.ali.5209@gmail.com", GMAIL_USER)

previous_status = {ip: True for ip in DNS_SERVERS}


def send_gmail(subject, body):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not GMAIL_TO:
        print("Missing Gmail settings. Set GMAIL_USER, GMAIL_APP_PASSWORD, and GMAIL_TO.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_TO
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print("Gmail notification sent")
    except Exception as e:
        print("Gmail error:", e)


def check_dns(ip):
    command = [
        "dig",
        f"@{ip}",
        QUERY,
        "+time=3",
        "+tries=1",
        "+short"
    ]

    start = time.time()

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )

        response_time = round((time.time() - start) * 1000, 2)

        if result.returncode == 0 and result.stdout.strip():
            return True, response_time

        return False, response_time

    except Exception:
        return False, None


while True:
    print("\n" + "=" * 60)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    for ip in DNS_SERVERS:
        status, response_time = check_dns(ip)

        if status:
            print(f"[UP]   {ip}   {response_time} ms")

            if previous_status[ip] is False:
                message = (
                    f"✅ DNS RECOVERED\n\n"
                    f"Server: {ip}\n"
                    f"Status: UP\n"
                    f"Response: {response_time} ms\n"
                    f"Time: {datetime.now()}"
                )
                send_gmail("DNS RECOVERED", message)

            previous_status[ip] = True

        else:
            print(f"[DOWN] {ip}")

            if previous_status[ip] is True:
                message = (
                    f"🚨 DNS DOWN\n\n"
                    f"Server: {ip}\n"
                    f"Port: 53\n"
                    f"Query: {QUERY}\n"
                    f"Status: NO RESPONSE\n"
                    f"Time: {datetime.now()}"
                )
                send_gmail("DNS DOWN", message)

            previous_status[ip] = False

    time.sleep(CHECK_INTERVAL)