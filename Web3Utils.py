import time
from web3 import Web3, HTTPProvider
from ServerConfig import *
from LogUtil import *

# web3 provider 最大重连次数
MAX_WEB3_AUTO_RECONNECT_ATTEMPTS = 5

web3 = None

def getWeb3():
    global web3

    if (not (web3 is None)):
        is_connected = web3.isConnected()
        if is_connected:
            return web3

    for attempt in range(MAX_WEB3_AUTO_RECONNECT_ATTEMPTS):
        try:
            web3 = Web3(HTTPProvider(GET_GETH_CONNECT_URL(), request_kwargs={'timeout': 15}))
            if web3 is None:
                error('getWeb3 none, try connect web3 times: %d', attempt + 1)
                raise(Exception('try connect web3 none'))

            is_connected = web3.isConnected()
            if is_connected:
                return web3
            else:
                error('getWeb3 not connected, try connect web3 times: %d', attempt + 1)
                raise(Exception('try connect web3 fail'))
        except (Exception) as e:
            wait_t = 0.5 * pow(2, attempt)
            error('getWeb3 fail attempt: %d, e: %s, wait_t: %.1f', attempt, e, wait_t)
            time.sleep(wait_t)

    fatal('web3 reconnect attempt totally fail, attempt: %d', attempt)
    return web3

def getWeb3ByGethUrl(geth_url):
    for attempt in range(MAX_WEB3_AUTO_RECONNECT_ATTEMPTS):
        try:
            _web3 = Web3(HTTPProvider(geth_url, request_kwargs={'timeout': 15}))
            if _web3 is None:
                error('getWeb3ByGethUrl none, try connect web3 times: %d', attempt + 1)
                raise(Exception('try connect web3 none'))

            is_connected = _web3.isConnected()
            if is_connected:
                return _web3
            else:
                error('getWeb3ByGethUrl not connected, try connect web3 times: %d', attempt + 1)
                raise(Exception('try connect web3 fail'))
        except (Exception) as e:
            wait_t = 0.5 * pow(2, attempt)
            error('getWeb3ByGethUrl fail attempt: %d, e: %s, wait_t: %.1f', attempt, e, wait_t)
            time.sleep(wait_t)

    fatal('web3 reconnect attempt totally fail, attempt: %d', attempt)
    return _web3
