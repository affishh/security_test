import os
from zapv2 import ZAPv2
import time

target = os.getenv("TARGET_URL", "http://localhost:4000")
apikey = os.getenv("ZAP_API_KEY", "changeme")

zap = ZAPv2(apikey=apikey, proxies={'http': 'http://localhost:8090', 'https': 'http://localhost:8090'})

print(f"Accessing target: {target}")
zap.urlopen(target)

print("Starting spider scan...")
scan_id = zap.spider.scan(target)
time.sleep(2)

while int(zap.spider.status(scan_id)) < 100:
    print(f"Spider progress: {zap.spider.status(scan_id)}%")
    time.sleep(2)

print("Spider scan completed.")

print("Generating report...")
with open("zap_report.html", "w") as report:
    report.write(zap.core.htmlreport())
print("✅ Report saved as zap_report.html")
