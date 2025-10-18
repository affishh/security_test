#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the OWASP ZAP Project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#

import os
import sys
import time
import json
import argparse
from zapv2 import ZAPv2

ZAP_API_KEY = os.environ.get('ZAP_API_KEY', '')

def create_zap_session(zap, session_name):
    print(f"Creating session: {session_name}")
    zap.core.new_session(name=session_name, overwrite=True)

def wait_for_passive_scan(zap):
    print("Waiting for passive scan to complete")
    while int(zap.pscan.records_to_scan) > 0:
        print(f"Records to scan: {zap.pscan.records_to_scan}")
        time.sleep(2)
    print("Passive scan complete")

def wait_for_active_scan(zap, scan_id):
    print(f"Waiting for active scan {scan_id} to complete")
    while int(zap.ascan.status(scan_id)) < 100:
        print(f"Active scan progress: {zap.ascan.status(scan_id)}%")
        time.sleep(5)
    print("Active scan complete")

def check_zap_client_version():
    # Dummy function to avoid the error.
    # You can implement actual version checking if you want.
    pass


def main():
    parser = argparse.ArgumentParser(description='OWASP ZAP baseline scan helper.')
    parser.add_argument('-t', '--target', required=True, help='Target URL to scan')
    parser.add_argument('-r', '--report', required=True, help='File to save HTML report')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-I', '--ignore-redirects', action='store_true', help='Ignore redirects')

    args = parser.parse_args()

    zap = ZAPv2(apikey=ZAP_API_KEY)

    create_zap_session(zap, 'default-session')

    print(f"Accessing target {args.target}")
    zap.urlopen(args.target)
    time.sleep(2)

    wait_for_passive_scan(zap)

    print("Starting active scan")
    scan_id = zap.ascan.scan(args.target)

    wait_for_active_scan(zap, scan_id)

    print(f"Generating report to {args.report}")
    report = zap.core.htmlreport()
    with open(args.report, 'w') as f:
        f.write(report)

if __name__ == "__main__":
    main()
