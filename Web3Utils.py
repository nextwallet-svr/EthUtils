import time
from web3 import Web3, HTTPProvider
from ServerConfig import *
from LogUtil import *
from web3.middleware import geth_poa_middleware

if CURR_ETH_NETWORK == "main":
    from web3.auto.infura import w3
else:
    from web3.auto.infura.ropsten import w3

MAX_WEB3_AUTO_RECONNECT_ATTEMPTS = 5

web3 = None

def getWeb3():
    global web3

    if INFURA_API_SWITCH_ON:
        web3 = w3
        is_connected = web3.isConnected()
        if is_connected:
            info('infura connect web3: %s', str(web3))
            return web3
        else:
            error('infura not connect web3: %s', str(web3))
            return web3
    else:
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

