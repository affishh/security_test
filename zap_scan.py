from zapv2 import ZAPv2
import os
import time

target = os.getenv("TARGET_URL")
apikey = os.getenv("ZAP_API_KEY")
zap_host = os.getenv('ZAP_HOST', 'zap') 

ap = ZAPv2(apikey=api_key, proxies={'http': f'http://{zap_host}:8090', 'https': f'http://{zap_host}:8090'})


print(f"Scanning target: {target}")
zap.urlopen(target)
zap.spider.scan(target)
time.sleep(2)

scan_id = zap.ascan.scan(target)
while int(zap.ascan.status(scan_id)) < 100:
    print(f"Scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(5)

print("Scan complete.")
with open("zap_report.html", "w") as f:
    f.write(zap.core.htmlreport())
