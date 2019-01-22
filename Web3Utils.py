import time
from web3 import Web3, HTTPProvider
from ServerConfig import *
from LogUtil import *
from web3.middleware import geth_poa_middleware

MAX_WEB3_AUTO_RECONNECT_ATTEMPTS = 5
WEB3_CONNECT_TIMEOUT_S = 15

web3 = None
ws_web3 = None

def getInfuraWsWeb3():
    global ws_web3

    # INFURA¿ª¹ØÎ´¿ª
    if not INFURA_API_SWITCH_ON:
        return None

    #
    if ws_web3 and ws_web3.isConnected():
        return ws_web3

    for attempt in range(MAX_WEB3_AUTO_RECONNECT_ATTEMPTS):
        try:
            ws_web3 = Web3(Web3.WebsocketProvider(GET_INFURA_CONNECT_WS_URL(), websocket_kwargs={'timeout': WEB3_CONNECT_TIMEOUT_S}))
            if not ws_web3:
                error('getInfuraWsWeb3 fail, try connect ws_web3 times: %d, WS_URL: %s', attempt + 1, GET_INFURA_CONNECT_WS_URL())
                raise(Exception('try connect ws_web3 none'))

            if ws_web3.isConnected():
                return ws_web3

            error('getInfuraWsWeb3 fail, try connect ws_web3 times: %d, WS_URL: %s', attempt + 1, GET_INFURA_CONNECT_WS_URL())
            raise(Exception('try connect ws_web3 fail'))
        except (Exception) as e:
            wait_t = 0.5 * pow(2, attempt)
            error('getInfuraWsWeb3 fail attempt: %d, e: %s, wait_t: %.1f, WS_URL: %s', attempt, e, wait_t, GET_INFURA_CONNECT_WS_URL())
            time.sleep(wait_t)

    fatal('getInfuraWsWeb3 reconnect attempt totally fail, attempt: %d, WS_URL: %s', attempt, GET_INFURA_CONNECT_WS_URL())
    return ws_web3

def getWeb3():
    global web3

    if web3 and web3.isConnected():
        return web3

    for attempt in range(MAX_WEB3_AUTO_RECONNECT_ATTEMPTS):
        try:
            web3 = Web3(HTTPProvider(GET_GETH_CONNECT_URL(), request_kwargs={'timeout': WEB3_CONNECT_TIMEOUT_S}))
            if not web3:
                error('getWeb3 none, try connect web3 times: %d, CONNECT_URL: %s', attempt + 1, GET_GETH_CONNECT_URL())
                raise(Exception('try connect web3 none'))

            if web3.isConnected():
                return web3

            error('getWeb3 not connected, try connect web3 times: %d, CONNECT_URL: %s', attempt + 1, GET_GETH_CONNECT_URL())
            raise(Exception('try connect web3 fail'))
        except (Exception) as e:
            wait_t = 0.5 * pow(2, attempt)
            error('getWeb3 fail attempt: %d, e: %s, wait_t: %.1f, CONNECT_URL: %s', attempt, e, wait_t, GET_GETH_CONNECT_URL())
            time.sleep(wait_t)

    fatal('web3 reconnect attempt totally fail, attempt: %d, CONNECT_URL: %s', attempt, GET_GETH_CONNECT_URL())
    return web3

def getWeb3Poa(_geth_url = None):
    for attempt in range(MAX_WEB3_AUTO_RECONNECT_ATTEMPTS):
        try:
            geth_url = None
            if _geth_url is None:
                geth_url = GET_GETH_CONNECT_URL()
            else:
                geth_url = _geth_url

            _web3 = Web3(HTTPProvider(geth_url, request_kwargs={'timeout': 15}))
            if _web3 is None:
                error('getWeb3Poa none, try connect web3 times: %d', attempt + 1)
                raise(Exception('try connect web3 none'))

            _web3.middleware_stack.inject(geth_poa_middleware, layer=0)

            is_connected = _web3.isConnected()
            if is_connected:
                return _web3
            else:
                error('getWeb3Poa not connected, try connect web3 times: %d', attempt + 1)
                raise(Exception('try connect web3 fail'))
        except (Exception) as e:
            wait_t = 0.5 * pow(2, attempt)
            error('getWeb3Poa fail attempt: %d, e: %s, wait_t: %.1f', attempt, e, wait_t)
            time.sleep(wait_t)

    fatal('web3 reconnect attempt totally fail, attempt: %d', attempt)
    return _web3
