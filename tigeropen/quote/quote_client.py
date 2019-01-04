# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import re
import delorean
import six

from tigeropen.common.consts import THREAD_LOCAL, SecurityType
from tigeropen.common.exceptions import ApiException
from tigeropen.quote.response.future_briefs_response import FutureBriefsResponse
from tigeropen.quote.response.future_exchange_response import FutureExchangeResponse
from tigeropen.quote.response.future_contract_response import FutureContractResponse
from tigeropen.quote.response.future_quote_bar_response import FutureQuoteBarResponse
from tigeropen.quote.response.future_quote_ticks_response import FutureTradeTickResponse
from tigeropen.quote.response.future_trading_times_response import FutureTradingTimesResponse
from tigeropen.quote.response.option_briefs_response import OptionBriefsResponse
from tigeropen.quote.response.option_chains_response import OptionChainsResponse
from tigeropen.quote.response.option_expirations_response import OptionExpirationsResponse
from tigeropen.quote.response.option_quote_bar_response import OptionQuoteBarResponse
from tigeropen.quote.response.option_quote_ticks_response import OptionTradeTickResponse
from tigeropen.quote.response.quote_bar_response import QuoteBarResponse
from tigeropen.quote.response.quote_timeline_response import QuoteTimelineResponse
from tigeropen.quote.response.quote_brief_response import QuoteBriefResponse
from tigeropen.quote.response.stock_short_interest_response import ShortInterestResponse
from tigeropen.quote.response.symbol_names_response import SymbolNamesResponse
from tigeropen.quote.response.symbols_response import SymbolsResponse
from tigeropen.tiger_open_client import TigerOpenClient
from tigeropen.quote.request.model import MarketParams, SingleQuoteParams, MultipleQuoteParams, MultipleContractParams, \
    SingleFutureQuoteParams, FutureExchangeParams, FutureTypeParams, FutureTradingTimeParams, SingleContractParams, \
    SingleOptionQuoteParams
from tigeropen.quote.request import OpenApiRequest
from tigeropen.quote.response.quote_ticks_response import TradeTickResponse
from tigeropen.quote.response.market_status_response import MarketStatusResponse
from tigeropen.common.consts.service_types import MARKET_STATE, ALL_SYMBOLS, ALL_SYMBOL_NAMES, BRIEF, STOCK_DETAIL, \
    TIMELINE, KLINE, TRADE_TICK, OPTION_EXPIRATION, OPTION_CHAIN, FUTURE_EXCHANGE, OPTION_BRIEF, \
    OPTION_KLINE, OPTION_TRADE_TICK, FUTURE_KLINE, FUTURE_TICK, FUTURE_CONTRACT_BY_EXCHANGE_CODE, \
    FUTURE_CONTINUOUS_CONTRACTS, FUTURE_TRADING_DATE, QUOTE_SHORTABLE_STOCKS, FUTURE_REAL_TIME_QUOTE, \
    FUTURE_CURRENT_CONTRACT
from tigeropen.common.consts import Market, Language, QuoteRight, BarPeriod
from tigeropen.common.util.contract_utils import extract_option_info
from tigeropen.common.util.common_utils import eastern
import logging


class QuoteClient(TigerOpenClient):
    def __init__(self, client_config, logger=None):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        super(QuoteClient, self).__init__(client_config, logger=logger)
        if client_config:
            self._lang = client_config.language
        else:
            self._lang = Language.zh_CN

    def get_market_status(self, market=Market.ALL, lang=None):
        """
        获取市场状态
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MarketParams()
        params.market = market.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(MARKET_STATE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = MarketStatusResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.markets
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_symbols(self, market=Market.ALL):
        """
        获取股票代号列表
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :return:
        """
        params = MarketParams()
        params.market = market.value

        request = OpenApiRequest(ALL_SYMBOLS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SymbolsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.symbols
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_symbol_names(self, market=Market.ALL, lang=None):
        """
        获取股票代号列表和名称
        :param market: US 美股，HK 港股， CN A股，ALL 所有
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MarketParams()
        params.market = market.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(ALL_SYMBOL_NAMES, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = SymbolNamesResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.symbol_names
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_briefs(self, symbols, include_hour_trading=False, include_ask_bid=False, right=QuoteRight.BR, lang=None):
        """
        获取股票摘要
        :param symbols: 股票代号列表
        :param include_hour_trading: 是否包含盘前盘后
        :param include_ask_bid: 是否包含买卖盘
        :param right: 复权选项 ，br: 前复权，nr: 不复权
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.include_hour_trading = include_hour_trading
        params.include_ask_bid = include_ask_bid
        params.right = right.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(BRIEF, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBriefResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_details(self, symbols, lang=None):
        """
        获取股票详情(废弃)
        :param symbols: 股票代号列表
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(STOCK_DETAIL, biz_model=params)
        response_content = self.__fetch_data(request)
        return response_content

    def get_timeline(self, symbols, include_hour_trading=False, begin_time=-1, lang=None):
        """
        获取当日分时数据
        :param symbols: 股票代码
        :param include_hour_trading: 是否包含盘前盘后分时
        :param begin_time: 开始时间
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.include_hour_trading = include_hour_trading
        params.begin_time = begin_time
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(TIMELINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteTimelineResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.timelines
            else:
                raise ApiException(response.code, response.message)

    def get_bars(self, symbols, period=BarPeriod.DAY, begin_time=-1, end_time=-1, right=QuoteRight.BR, limit=251,
                 lang=None):
        """
        获取K线数据
        :param symbols: 股票代码
        :param period: day: 日K,week: 周K,month:月K ,year:年K,1min:1分钟,5min:5分钟,15min:15分钟,30min:30分钟,60min:60分钟
        :param begin_time: 开始时间
        :param end_time: 结束时间
        :param right: 复权选项 ，br: 前复权，nr: 不复权
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        if period:
            params.period = period.value
        params.begin_time = begin_time
        params.end_time = end_time
        params.right = right.value
        params.limit = limit
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = QuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_trade_ticks(self, symbols, begin_index=0, end_index=30, limit=30, lang=None):
        """
        获取逐笔成交
        :param symbols: 股票代码
        :param begin_index: 开始索引
        :param end_index: 结束索引
        :param limit: 数量限制
        :param lang: 语言支持: zh_CN,zh_TW,en_US
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(TRADE_TICK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = TradeTickResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trade_ticks
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_short_interest(self, symbols, lang=None):
        """
        获取美股的做空数据
        :param symbols: 股票列表
        :param lang:
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(QUOTE_SHORTABLE_STOCKS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ShortInterestResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.short_interests
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_expirations(self, symbols):
        """
        返回美股期权的过期日
        :param symbols: 股票列表
        :return:
        """
        params = MultipleQuoteParams()
        params.symbols = symbols

        request = OpenApiRequest(OPTION_EXPIRATION, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionExpirationsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.expirations
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_chain(self, symbol, expiry):
        """
        获取美股期权链
        :param symbol: 股票代码
        :param expiry: 过期日(类似2019-01-04或者1546578000000)
        :return:
        """
        params = MultipleContractParams()
        param = SingleContractParams()
        param.symbol = symbol
        if isinstance(expiry, six.string_types) and re.match('[0-9]{4}\-[0-9]{2}\-[0-9]{2}', expiry):
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
        else:
            param.expiry = expiry
        params.contracts = [param]
        request = OpenApiRequest(OPTION_CHAIN, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionChainsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.chain
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_briefs(self, identifiers):
        """
        获取期权最新行情
        :param identifiers: 期权代码
        :return:
        """
        params = MultipleContractParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.contracts = contracts

        request = OpenApiRequest(OPTION_BRIEF, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_option_bars(self, identifiers, begin_time=-1, end_time=4070880000000):
        """
        获取K线(DAY)数据
        :param identifiers: 期权代码
        :param begin_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        params = MultipleContractParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleOptionQuoteParams()
            param.symbol = symbol
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
            param.put_call = put_call
            param.strike = strike
            param.period = BarPeriod.DAY.value
            param.begin_time = begin_time
            param.end_time = end_time
            contracts.append(param)
        params.contracts = contracts

        request = OpenApiRequest(OPTION_KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionQuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_option_trade_ticks(self, identifiers):
        """
        获取期权逐笔成交
        :param identifiers: 期权代码
        :return:
        """
        params = MultipleContractParams()
        contracts = []
        for identifier in identifiers:
            symbol, expiry, put_call, strike = extract_option_info(identifier)
            if symbol is None or expiry is None or put_call is None or strike is None:
                continue
            param = SingleContractParams()
            param.symbol = symbol
            param.expiry = int(delorean.parse(expiry, timezone=eastern, dayfirst=False).datetime.timestamp() * 1000)
            param.put_call = put_call
            param.strike = strike
            contracts.append(param)
        params.contracts = contracts

        request = OpenApiRequest(OPTION_TRADE_TICK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OptionTradeTickResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trade_ticks
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_future_exchanges(self, sec_type=SecurityType.FUT, lang=None):
        """
        获取期货交易所列表
        :param sec_type: FUT/FOP
        :param lang:
        :return:
        """
        params = MarketParams()
        params.sec_type = sec_type.value
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(FUTURE_EXCHANGE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureExchangeResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.exchanges
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_contracts(self, exchange, lang=None):
        """
        获取交易所下的可交易合约
        :param exchange:
        :param lang:
        :return:
        """
        params = FutureExchangeParams()
        params.exchange_code = exchange
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(FUTURE_CONTRACT_BY_EXCHANGE_CODE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_continuous_future_contracts(self, future_type, lang=None):
        """
        查询指定品种的连续合约
        :param future_type: 期货合约对应的交易品种， 如 CL
        :param lang:
        :return:
        """
        params = FutureTypeParams()
        params.type = future_type
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(FUTURE_CONTINUOUS_CONTRACTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_current_future_contract(self, future_type, lang=None):
        """
        查询指定品种的当前合约
        :param future_type: 期货合约对应的交易品种， 如 CL
        :param lang:
        :return:
        """
        params = FutureTypeParams()
        params.type = future_type
        params.lang = lang.value if lang else self._lang.value

        request = OpenApiRequest(FUTURE_CURRENT_CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureContractResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_trading_times(self, contract_code, trading_date=None):
        """
        查询指定期货合约的交易时间
        :param contract_code:
        :param trading_date:
        :return:
        """
        params = FutureTradingTimeParams()
        params.contract_code = contract_code
        params.trading_date = trading_date

        request = OpenApiRequest(FUTURE_TRADING_DATE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureTradingTimesResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trading_times
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_future_bars(self, symbol, period=BarPeriod.DAY, begin_time=-1, end_time=-1, limit=1000):
        """
        获取期货K线数据
        :param symbol: 股票代码
        :param period: day: 日K,week: 周K,month:月K ,year:年K,1min:1分钟,5min:5分钟,15min:15分钟,30min:30分钟,60min:60分钟
        :param begin_time: 开始时间
        :param end_time: 结束时间
        :param limit: 数量限制
        :return:
        """
        params = SingleFutureQuoteParams()
        params.contract_code = symbol
        if period:
            params.period = period.value
        params.begin_time = begin_time
        params.end_time = end_time
        params.limit = limit

        request = OpenApiRequest(FUTURE_KLINE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureQuoteBarResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.bars
            else:
                raise ApiException(response.code, response.message)

    def get_future_trade_ticks(self, symbol, begin_index=0, end_index=30, limit=1000):
        """
        获取期货逐笔成交
        :param symbol: 股票代码
        :param begin_index: 开始索引
        :param end_index: 结束索引
        :param limit: 数量限制
        :return:
        """
        params = SingleFutureQuoteParams()
        params.contract_code = symbol
        params.begin_index = begin_index
        params.end_index = end_index
        params.limit = limit

        request = OpenApiRequest(FUTURE_TICK, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureTradeTickResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.trade_ticks
            else:
                raise ApiException(response.code, response.message)

    def get_future_brief(self, identifier):
        """
        获取期货最新行情
        :param identifier: 期货代码
        :return:
        """
        params = SingleFutureQuoteParams()
        params.contract_code = identifier

        request = OpenApiRequest(FUTURE_REAL_TIME_QUOTE, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = FutureBriefsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.briefs
            else:
                raise ApiException(response.code, response.message)

    def __fetch_data(self, request):
        try:
            response = super(QuoteClient, self).execute(request)
            return response
        except Exception as e:
            if THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e
