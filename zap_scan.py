from zapv2 import ZAPv2
import time
import os
from zapv2 import ZAPv2

target = os.getenv('TARGET_URL')
api_key = os.getenv('ZAP_API_KEY')

print(f"Accessing target: {target}")

zap = ZAPv2(apikey=api_key, proxies={'http': 'http://localhost:8090', 'https': 'http://localhost:8090'})

print(f"Accessing target: {target}")

try:
    zap.urlopen(target)
    time.sleep(2)

    print("Starting spider scan...")
    spider_id = zap.spider.scan(target)
    time.sleep(2)

    while int(zap.spider.status(spider_id)) < 100:
        print(f"Spider progress: {zap.spider.status(spider_id)}%")
        time.sleep(2)

    print("Spider complete. Starting active scan...")
    ascan_id = zap.ascan.scan(target)
    while int(zap.ascan.status(ascan_id)) < 100:
        print(f"Active scan progress: {zap.ascan.status(ascan_id)}%")
        time.sleep(5)

    print("Generating report...")
    report = zap.core.htmlreport()
    with open("zap_report.html", "w") as f:
        f.write(report)

    print("✅ ZAP scan completed and report saved.")
except Exception as e:
    print(f"❌ ZAP scan failed: {e}")
    exit(1)
