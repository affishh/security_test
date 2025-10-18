import os
import time
from zapv2 import ZAPv2

target = os.getenv("TARGET_URL", "http://nodeapp:4000")
apikey = os.getenv("ZAP_API_KEY", "")
zap_host = os.getenv("ZAP_HOST", "zap")

zap = ZAPv2(apikey=apikey, proxies={
    'http': f'http://{zap_host}:8090',
    'https': f'http://{zap_host}:8090'
})

print(f"Accessing {target}")
zap.urlopen(target)

print("Starting scan...")
scan_id = zap.ascan.scan(target)
while int(zap.ascan.status(scan_id)) < 100:
    print(f"Scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(5)

print("Scan completed.")
with open("zap_report.html", "w") as f:
    f.write(zap.core.htmlreport())
