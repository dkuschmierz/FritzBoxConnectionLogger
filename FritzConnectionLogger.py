from itertools import count

from fritzconnection import FritzConnection
from fritzconnection.lib.fritzstatus import FritzStatus
from fritzconnection.core.exceptions import FritzServiceError
from datetime import datetime
import argparse
import time
import signal
import sys
import csv

def signal_handler(sig, frame):
    print('Program closed by user')
    sys.exit(0)

def main(args):
    signal.signal(signal.SIGINT, signal_handler)
    
    kwargs = dict(address=args.address, port=args.port, user=args.user, password=args.password, timeout=args.timeout, use_tls=args.encryption)
    fc = FritzConnection(**{k: v for k, v in kwargs.items() if v is not None})
    fs = FritzStatus(fc)
    
    print("\nExit program by pressing Ctrl+C\n")
    if args.verbose:
        print("      Timestamp      | PhyLink | Sync | Cur. Upstream | Cur. Downstream | Max. Upstream | Max. Downstream | Line Capacity Up | Line Capacity Down | SNR Up  | SNR Down | Att. Up | Att. Down")
        print(" -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    
    with open(args.output, 'w', newline='') as csvFile:
        fieldNames = ['Timestamp','PhyLink','Sync','Cur. Upstream','Cur. Downstream','Max. Upstream','Max. Downstream','Line Capacity Up','Line Capacity Down','SNR Up','SNR Down','Att. Up','Att. Down']
        csvWriter = csv.DictWriter(csvFile,fieldnames=fieldNames)
        csvWriter.writeheader()

        while True:
            att_upstream, att_downstream = fs.str_attenuation
            snr_upstream, snr_downstream = fs.str_noise_margin
            curstream_up, curstream_down = fs.str_transmission_rate
            maxstream_up, maxstream_down = fs.str_max_bit_rate
            line_up, line_down = fs.str_max_linked_bit_rate
            
            dataDict = {
                'Timestamp': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'PhyLink' : fs.is_connected,
                'Sync' : fs.is_linked,
                'Cur. Upstream' : curstream_up,
                'Cur. Downstream' : curstream_down,
                'Max. Upstream' : maxstream_up,
                'Max. Downstream' : maxstream_down,
                'Line Capacity Up' : line_up,
                'Line Capacity Down' : line_down,
                'SNR Up' : snr_upstream,
                'SNR Down' : snr_downstream,
                'Att. Up' : att_upstream,
                'Att. Down' : att_downstream
            }
            
            csvWriter.writerow(dataDict)
            
            if args.verbose:               
                print(" {0:<19} | {1:<7} | {2:<4} | {3:<13} | {4:<15} | {5:<13} | {6:<15} |  {7:<15} | {8:<18} | {9:<7} | {10:<8} | {11:<7} | {12:<8}".format(datetime.now().strftime("%d.%m.%Y %H:%M:%S"),fs.is_connected, fs.is_linked, curstream_up, curstream_down, maxstream_up , maxstream_down, line_up, line_down, snr_upstream, snr_downstream, att_upstream, att_downstream))
            time.sleep(args.cycleTime)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments for the WanConnectionLogger module')
    parser.add_argument('-a', '--address', dest= 'address', help='IP-Address of the router')
    parser.add_argument('-c', '--cycle-time', type=int, default=120, dest= 'cycleTime', help='Cycle time to gather data in seconds. Default is 120s')
    parser.add_argument('-e', '--encryption', dest= 'encryption', type=bool, help='Use encrypted connetion')
    parser.add_argument('-o', '--output', type=str , default= "./FritzConnectionLog.csv", dest= 'output', help='Path to output file. Defaults to ./FritzConnectionLog.csv')
    parser.add_argument('-p', '--password', dest= 'password', help='Password for login')
    parser.add_argument('-P', '--port', dest= 'port', help='Port for connection')
    parser.add_argument('-t', '--timeout', dest= 'timeout', help='Timeout for establashing connection')
    parser.add_argument('-u', '--user', dest= 'user', help='Username for login')
    parser.add_argument('-v', '--verbose', action="store_true", default=False, dest= 'verbose', help='Print data also to console')
    
    args = parser.parse_args()
    
    main(args)