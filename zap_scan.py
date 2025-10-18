from zapv2 import ZAPv2
import os
import time

target = os.getenv("TARGET_URL")
apikey = os.getenv("ZAP_API_KEY")

zap = ZAPv2(apikey=apikey, proxies={'http': 'http://localhost:8090', 'https': 'http://localhost:8090'})

print(f"Scanning target: {target}")
zap.urlopen(target)
time.sleep(2)

scan_id = zap.ascan.scan(target)
while int(zap.ascan.status(scan_id)) < 100:
    print(f"Scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(5)

print("Scan complete.")
with open("zap_report.html", "w") as f:
    f.write(zap.core.htmlreport())
