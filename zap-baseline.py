#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
from zapv2 import ZAPv2

ZAP_API_KEY = os.environ.get('ZAP_API_KEY', '')

def create_zap_session(zap, session_name, debug=False):
    if debug:
        print(f"[DEBUG] Creating session: {session_name}")
    zap.core.new_session(name=session_name, overwrite=True)

def wait_for_passive_scan(zap, debug=False):
    print("Waiting for passive scan to complete...")
    while int(zap.pscan.records_to_scan) > 0:
        if debug:
            print(f"[DEBUG] Records to scan: {zap.pscan.records_to_scan}")
        time.sleep(2)
    print("Passive scan complete.")

def wait_for_active_scan(zap, scan_id, debug=False):
    print(f"Waiting for active scan {scan_id} to complete...")
    while int(zap.ascan.status(scan_id)) < 100:
        if debug:
            print(f"[DEBUG] Active scan progress: {zap.ascan.status(scan_id)}%")
        time.sleep(5)
    print("Active scan complete.")

def main():
    parser = argparse.ArgumentParser(description='OWASP ZAP baseline scan helper.')
    parser.add_argument('-t', '--target', required=True, help='Target URL to scan')
    parser.add_argument('-r', '--report', required=True, help='File to save HTML report')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-I', '--ignore-redirects', action='store_true', help='Ignore redirects')

    args = parser.parse_args()

    try:
        zap = ZAPv2(apikey=ZAP_API_KEY)

        create_zap_session(zap, 'default-session', debug=args.debug)

        if args.ignore_redirects:
            if args.debug:
                print("[DEBUG] Disabling handling of redirects in active scan")
            zap.ascan.set_option_handle_redirects(False)

        print(f"Accessing target {args.target}")
        zap.urlopen(args.target)
        time.sleep(2)

        wait_for_passive_scan(zap, debug=args.debug)

        print("Starting active scan...")
        scan_id = zap.ascan.scan(args.target)

        wait_for_active_scan(zap, scan_id, debug=args.debug)

        print(f"Generating report to {args.report}")
        report = zap.core.htmlreport()
        with open(args.report, 'w') as f:
            f.write(report)

        print("Scan completed successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
