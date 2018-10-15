import json
import time
import datetime
import traceback
import hexbytes
from eth_utils import *
from web3 import Web3, HTTPProvider, IPCProvider, datastructures
from .Web3Utils import *
from LogUtil import *

class TxReceiptException(Exception):
    pass


class JSONEncoder(json.JSONEncoder):
    '''处理ObjectId,该类型无法转为json'''
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datastructures.AttributeDict):
            return dict(o)
        elif isinstance(o, hexbytes.HexBytes):
            return o.hex()
        return json.JSONEncoder.default(self, o)


JSEncoder = JSONEncoder()

######################################################################
#判断一个地址是否是合约地址
def isContractAddress(address):
    try:
        if (address is None or address == ''):
            debug('isContractAddress, invalid address: %s', str(address))
            return False

        code = getWeb3().eth.getCode(address)
        if code is None:
            error('getCode none, address: %s', address)
            raise(Exception('WEB3_DISCONNECT'))

        if code.hex() == '0x':
            return False
        else:
            return True
    except (Exception) as e:
        debug('isContractAddress except: address %s, %s', address, e)
        raise(e)

def convertHexBytes2Str(param):
    try:
        param_str = param.hex() if not isinstance(param, str) else param
        return param_str
    except (Exception) as e:
        error('convertHexBytes2Str: %s, %s', e, str(param))
        raise(e)

def convert2ChecksumAddr(addr):
    try:
        chksm_addr = '' if (addr is None) else to_checksum_address(addr)
        return chksm_addr
    except (Exception) as e:
        error('convert2ChecksumAddr: %s, %s', e, addr)
        raise(e)

def unpaddedAddress(address):
    if len(address) <= 42:
        return address;
    try:
        unpadded_addr = convert2ChecksumAddr('0x' + address[-40:])
        return unpadded_addr
    except (Exception) as e:
        error('unpaddedAddress except: %s, address: %s', e, address)
    return None

def convertDictHexBytes2Str(d):
    for key, value in d.items():
        if type(value) is hexbytes.main.HexBytes:
            d[key] = value.hex()
        if type(value) is list:
            new_value = []
            for e in value:
                if type(e) is hexbytes.main.HexBytes:
                    new_value.append(e.hex())
                else:
                    new_value.append(e)
            d[key] = new_value
    return d

def leftUnPad4Address(s):
    if len(s) <= 40:
        return s
    else:
        return s[-40:]

def rightUnPad4Str(s, reserve_len):
    if reserve_len == 0:
        return s
    if len(s) <= reserve_len:
        return s
    return s[:reserve_len]

def tryGetTxByHash(tx_hash):
    raw_tx = None
    for i in range(1):
        raw_tx = getWeb3().eth.getTransaction(tx_hash)
        if (raw_tx is None):
            error('retry GetTxByHash, hash: %s, retry times: %d', tx_hash, i)
            continue
        else:
            break
    return raw_tx

def tryGetTxReceiptByHash(tx_hash):
    raw_tx_receipt = None
    for i in range(1):
        raw_tx_receipt = getWeb3().eth.getTransactionReceipt(tx_hash)
        if (raw_tx_receipt is None):
            error('retry GetTxReceiptByHash, hash: %s, retry times: %d', tx_hash, i)
            continue
        else:
            break
    return raw_tx_receipt

def getTransactionByHash(tx_hash):
    tx_dict = None
    try:
        raw_tx = tryGetTxByHash(tx_hash)
        if raw_tx is None:
            raise Exception("SERVER_INTERNAL_ERR")
        tx_dict = convertDictHexBytes2Str(dict(raw_tx))
        tx_dict['from'] = convert2ChecksumAddr(tx_dict['from'])
        tx_dict['to'] = convert2ChecksumAddr(tx_dict['to'])
    except (Exception) as e:
        debug('getTransactionByHash: e: %s, tx_hash: %s', e, tx_hash)
        # raise (e)
        return None
    return tx_dict

def getTransactionReceiptByHash(tx_hash):
    tx_receipt_dict = None
    try:
        raw_tx_receipt = tryGetTxReceiptByHash(tx_hash)
        if raw_tx_receipt is None:
            raise Exception("SERVER_INTERNAL_ERR")
        tx_receipt_dict = convertDictHexBytes2Str(dict(raw_tx_receipt))
        tx_receipt_dict['from'] = convert2ChecksumAddr(tx_receipt_dict['from'])
        tx_receipt_dict['to'] = convert2ChecksumAddr(tx_receipt_dict['to'])
        tx_receipt_dict['contractAddress'] = convert2ChecksumAddr(tx_receipt_dict['contractAddress'])
    except (Exception) as e:
        debug('getTransactionReceiptByHash: e: %s, tx_hash: %s', e, tx_hash)
        # raise (e)
        return None
    return json.loads(JSEncoder.encode(tx_receipt_dict))

def get_input_method_signature(input):
    tmp_input = add_0x_prefix(input)
    if len(tmp_input) < 10:
        return ''
    return tmp_input[:10]

def get_block_with_retry(block_num_or_hash, max_retry=3, interval=0.5):
    block = getWeb3().eth.getBlock(block_num_or_hash)
    while block is None and max_retry > 0:
        error("getblock %s failed, retry after %s sec, max retry %s" %
              (block_num_or_hash, interval, max_retry))
        time.sleep(interval)
        max_retry -= 1
        block = getWeb3().eth.getBlock(block_num_or_hash)
    return block

g_filter_map = {}

def destroyFilter(filter):
    global g_filter_map
    if filter:
        ret = getWeb3().eth.uninstallFilter(filter.filter_id)
        if not ret:
            error("uninstallFilter fail, filter.filter_id: %s", str(filter.filter_id))
        else:
            g_filter_map.pop(filter.filter_id)
        return ret

def createFilter(contract_event_obj, from_block_number, to_block_number, tag):
    global g_filter_map
    filter_func = getattr(contract_event_obj, 'createFilter')
    filter = filter_func(fromBlock=from_block_number, toBlock=to_block_number)
    if not filter:
        error("createFilter fail, from_block_number: %d, to_block_number: %d",
                from_block_number, to_block_number)
    else:
        g_filter_map[filter.filter_id] = tag
    return filter
