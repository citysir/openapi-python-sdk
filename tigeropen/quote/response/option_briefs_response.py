# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import six
import pandas as pd
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string

COLUMNS = ['identifier', 'symbol', 'expiry', 'strike', 'put_call', 'multiplier', 'ask_price', 'ask_size', 'bid_price',
           'bid_size', 'pre_close', 'latest_price', 'latest_time', 'volume', 'open_interest', 'open', 'high', 'low']
BRIEF_FIELD_MAPPINGS = {'askPrice': 'ask_price', 'askSize': 'ask_size', 'bidPrice': 'bid_price', 'bidSize': 'bid_size',
                        'latestPrice': 'latest_price', 'openInterest': 'open_interest', 'preClose': 'pre_close',
                        'right': 'put_call', 'latestTime': 'latest_time'}


class OptionBriefsResponse(TigerResponse):
    def __init__(self):
        super(OptionBriefsResponse, self).__init__()
        self.briefs = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            brief_data = []
            for item in self.data:
                item_values = {}
                for key, value in item.items():
                    if value is None:
                        continue
                    if isinstance(value, six.string_types):
                        value = get_string(value)
                    if key == 'right':
                        value = value.upper()
                    tag = BRIEF_FIELD_MAPPINGS[key] if key in BRIEF_FIELD_MAPPINGS else key
                    item_values[tag] = value
            brief_data.append([item_values.get(tag) for tag in COLUMNS])

            self.briefs = pd.DataFrame(brief_data, columns=COLUMNS)
