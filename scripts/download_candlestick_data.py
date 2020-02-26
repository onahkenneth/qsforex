from __future__ import print_function

try:
    import Queue as queue
except ImportError:
    import queue

from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import logging
import json
import sys
import os
import pytz
import requests

from datetime import datetime
from qsforex.data.candle import CandleSticks
from qsforex import settings


class HistoricCandlesticks(CandleSticks):
    def __init__(
            self, start_dt, end_dt, domain,
            access_token, account_id, pair
    ):
        super(HistoricCandlesticks, self).__init__(
            domain,
            access_token,
            account_id,
            pair,
            queue.Queue(),
            start_dt
        )
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.pair = pair
        self.logger = logging.getLogger(__name__)

    def connect_to_api(self):
        p = self.pair
        pair_oanda = "%s_%s" % (p[:3], p[3:])
        try:
            requests.packages.urllib3.disable_warnings()
            s = requests.Session()
            url = "https://" + self.domain + "/v3/instruments/" + pair_oanda + "/candles"
            headers = {'Authorization': 'Bearer ' + self.access_token}
            params = {
                'price': 'BA',
                'granularity': 'D',
                'from': self.start_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'to': self.end_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=True, verify=False)
            return resp
        except Exception as e:
            s.close()
            print("Caught exception when connecting to stream\n" + str(e))

    def download_data(self):
        response = self.connect_to_api()
        if response.status_code != 200:
            return False
        for line in response.iter_lines(1):
            if line:
                try:
                    d_line = line.decode('utf-8')
                    msg = json.loads(d_line)
                except Exception as e:
                    self.logger.error(
                        "Caught exception when converting message into json: %s" % str(e)
                    )
                    return False
                if "instrument" in msg and "candles" in msg:
                    self.logger.debug(msg)
                    getcontext().rounding = ROUND_HALF_DOWN
                    instrument = msg["instrument"].replace("_", "")
                    candles = msg["candles"]

                    for candle in candles:
                        ask = candle["ask"]
                        bid = candle["bid"]
                        time = datetime.strptime(candle["time"][:-4]+'Z', "%Y-%m-%dT%H:%M:%S.%fZ")
                        outfile = open(
                            os.path.join(
                                settings.CSV_DATA_DIR,
                                "%s_%s.csv" % (
                                    instrument, time.strftime("%Y%m%d")
                                )
                            ),
                            "w")
                        outfile.write("Time,Ask,Bid,AskVolume,BidVolume\n")
                        # Create the random walk for the bid/ask prices
                        # with fixed spread between them
                        line = "%s,%s,%s,%s,%s\n" % (
                            time.strftime("%d.%m.%Y %H:%M:%S.%f")[:-4],
                            "%0.5f" % float(ask["c"]), "%0.5f" % float(bid["c"]),
                            "%0.2f00" % candle["volume"], "%0.2f00" % candle["volume"]
                        )
                        outfile.write(line)


if __name__ == "__main__":
    try:
        timezone = pytz.utc
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        pair = sys.argv[3]

        start_date = timezone.localize(datetime.strptime(start_date, "%Y-%m-%d"))
        end_date = timezone.localize(datetime.strptime(end_date, "%Y-%m-%d"))

        candle_stick = HistoricCandlesticks(
            start_date,
            end_date,
            settings.API_DOMAIN,
            settings.ACCESS_TOKEN,
            settings.ACCOUNT_ID,
            pair
        )
        if candle_stick.download_data() is not False:
            print("Candlesticks data downloaded successfully")
        else:
            print("Candlesticks data download was unsuccessfully")
    except IndexError:
        print("You need to enter a start date, end date and currency pair, " +
              " e.g. 2019-01-01 2019-12-31 GBPUSD, as a command line parameter.")
        exit()
    except Exception:
        print("An error was encountered while processing request")
        exit()
