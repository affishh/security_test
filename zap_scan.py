import os
from zapv2 import ZAPv2
import time

target = os.environ.get("TARGET_URL")
apikey = os.environ.get("ZAP_API_KEY")
zap_host = os.environ.get("ZAP_HOST", "zap")

print(f"Accessing {target}")

zap = ZAPv2(apikey=apikey, proxies={'http': f'http://{zap_host}:8090', 'https': f'http://{zap_host}:8090'})

try:
    # Wait for ZAP to be ready
    for i in range(120):  # Increased wait time
        try:
            if int(zap.core.version):
                print("✅ Connected to ZAP!")
                break
        except:
            print("⏳ Waiting for ZAP to be ready...")
            time.sleep(2)

    print("Starting scan...")
    zap.urlopen(target)
    time.sleep(2)
    scan_id = zap.ascan.scan(target)

    while int(zap.ascan.status(scan_id)) < 100:
        print(f"Scan progress: {zap.ascan.status(scan_id)}%")
        time.sleep(2)

    print("Scan complete.")
    with open("zap_report.html", "w") as f:
        f.write(zap.core.htmlreport())

except Exception as e:
    print(f"Error: {e}")