from zapv2 import ZAPv2
import time

target = 'http://localhost:4000'
apikey = 'changeme'
zap = ZAPv2(apikey=apikey, proxies={'http': 'http://localhost:8090', 'https': 'http://localhost:8090'})

print('Accessing target...')
zap.urlopen(target)
time.sleep(2)

print('Starting Active Scan...')
scan_id = zap.ascan.scan(target)
while int(zap.ascan.status(scan_id)) < 100:
    print(f"Scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(2)

print('Scan completed.')
alerts = zap.core.alerts(baseurl=target)

# Save report
with open('zap_report.html', 'w') as f:
    f.write(zap.core.htmlreport())
print("ZAP report saved to zap_report.html")
