from zapv2 import ZAPv2
import time
import os

target = os.getenv('TARGET_URL', 'http://host.docker.internal:4000')
zap_api_key = os.getenv('ZAP_API_KEY', 'changeme')
zap = ZAPv2(apikey=zap_api_key, proxies={})  # No proxy! Direct API calls.

print(f"Accessing target: {target}")

try:
    zap.urlopen(target)
    time.sleep(2)

    print("Starting spider scan...")
    scan_id = zap.spider.scan(target)
    while int(zap.spider.status(scan_id)) < 100:
        print(f"Spider progress: {zap.spider.status(scan_id)}%")
        time.sleep(2)

    print("Spider completed. Starting active scan...")
    active_scan_id = zap.ascan.scan(target)
    while int(zap.ascan.status(active_scan_id)) < 100:
        print(f"Active scan progress: {zap.ascan.status(active_scan_id)}%")
        time.sleep(5)

    print("Scan completed. Generating report...")
    with open('zap_report.html', 'w') as f:
        f.write(zap.core.htmlreport())
    print("Report saved as zap_report.html")

except Exception as e:
    print("❌ ZAP scan failed:", e)
    exit(1)
