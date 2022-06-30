# TODO: Fix Constants
#import constants as Constants
import time
import csv
# from services.prometheus import PrometheusMessageSender
import subprocess
from datetime import datetime
import requests
import json

# URL='http://rancher-monitoring-prometheus.cattle-monitoring-system:9090/'
# USER='admin'
# PASSWORD='prom-operator'
# SLEEP_TIME=5
# MEASURE_TIME=20
# PROMETHEUS_PUSHER=None


def _ship_to_loki(msg):
    host = 'temporarytesting'
    curr_datetime = datetime.now()
    curr_datetime = curr_datetime.isoformat('T')

    # push msg log into grafana-loki
    url = 'http://192.168.122.189:3100/api/prom/push'
    headers = {
        'Content-type': 'application/json'
    }
    payload = {
        "streams": [
            {
                "stream": {
                    "host": host,
                    "job": "power_consumption_estimate"
                },
                "values": [
                    [ str(int(time.time())), "[INFO] " + msg ]
                ]
            }
        ]
    }
    payload = json.dumps(payload)
    print(payload)
    answer = requests.post(url, data=payload, headers=headers)
    print(answer)
    response = answer
    print(response)


def _scrape_csv_for_watts(csv_file_name=None):
    start_token = 'Usage;Device Name;PW Estimate'
    stop_token = '____________________________________________________________________'
    row_list = []
    printing = False
    overall_watts = 0.0
    with open(csv_file_name, mode='r') as csv_data:
        reader = csv.reader(csv_data)
        for row in reader:
            if start_token in row:
                printing = True
            if printing:
                if stop_token in row:
                    printing = False   
                else:
                    row_list.append(row)
    for item in row_list:
        mashed_power = item[0].split(';')
        if len(mashed_power) == 3 and (' mW ' in mashed_power[2] or ' W ' in mashed_power[2]):
            if 'mW' in mashed_power[2]:
                result_num = mashed_power[2].split(' mW')[0].strip()
                if result_num != 0:
                    true_num = int(result_num) / 1000
                    overall_watts = overall_watts + float(true_num)
            elif 'W' in mashed_power[2]:
                result_num = mashed_power[2].split(' W')[0].strip()
                if result_num != 0:
                    true_num = float(result_num)
                    overall_watts = overall_watts + true_num
    return overall_watts

def run():
    while True:
        time.sleep(3)
        subprocess.run(['/usr/sbin/powertop', '--quiet', '--csv=/tmp/report.csv', '--time=30'])
        input_file = '/tmp/report.csv'
        overall_watts_currently = _scrape_csv_for_watts(csv_file_name=input_file)
        _ship_to_loki('Current Estimated Watts Used: ' + str(overall_watts_currently))
        # now = int(time.time())
        # PROMETHEUS_PUSHER.push_to_gateway(gauge_name='Estimated Power Consumed', 
        #     gauge_help='estimated power consumption using powertop, needs work...', 
        #     batch_job_name='batch_'+str(now),
        #     gague_value=overall_watts_currently

        # )

#          *  *  *   Device Power Report   *  *  *

# Usage;Device Name;PW Estimate
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;CPU misc;  6.96 W   
#  18.1%;DRAM;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;CPU core;    0 mW   
#  18.1%;DRAM;    0 mW   
#  18.1%;CPU core;    0 mW  


if __name__ == '__main__':
    #PROMETHEUS_PUSHER=PrometheusMessageSender(url=URL, user=USER, password=PASSWORD)
    run()