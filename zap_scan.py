from zapv2 import ZAPv2
import time

target = 'http://nodeapp:4000'
apikey = 'changeme'

zap = ZAPv2(apikey=apikey, proxies={'http': 'http://zap:8090', 'https': 'http://zap:8090'})

print(f"Accessing {target}")
zap.urlopen(target)
time.sleep(2)

print("Spidering target...")
zap.spider.scan(target)
time.sleep(2)

while int(zap.spider.status) < 100:
    print(f"Spider progress: {zap.spider.status}%")
    time.sleep(1)

print("Scanning target...")
zap.ascan.scan(target)
while int(zap.ascan.status) < 100:
    print(f"Scan progress: {zap.ascan.status}%")
    time.sleep(2)

print("Generating report...")
with open("zap_report.html", "w") as f:
    f.write(zap.core.htmlreport())

print("Done.")
