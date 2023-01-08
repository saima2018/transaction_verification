# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/11/22 13:47
# @Author : masai
# @Email : sai.ma@spacexwalk.com
# @File : web3_py.py
# @Software: PyCharm
import json
import traceback

import web3.eth
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import ConciseContract

import binascii

ropsten = 'https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'
node1 = "http://192.168.1.111:8899"
node1_new = "https://chain.planckx.io/"

w3 = Web3(Web3.HTTPProvider(node1_new))
w3.middleware_onion.inject(geth_poa_middleware, layer=0) # for infura api

def str_to_hexStr(string):
    str_bin = string.encode('utf-8')
    return binascii.hexlify(str_bin).decode('utf-8')

def hexStr_to_str(hex_str):
    hexi = hex_str.encode('utf-8')
    str_bin = binascii.unhexlify(hexi)
    return str_bin.decode('utf-8')



def createAccount():
    password = input()
    w3.personal.newAccount(password)
    return

def getBalance(account):
    balance = w3.eth.getBalance(account)
    # print(balance)
    return balance

def sendTransaction(send_from=None, value = 0.0, gas = 2000000,
                    send_to=None, data=None, chain = None, Private_key = None):
    account = '0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2'
    pk = "e4c46fca983502aa39adae992600b82541dcfc393dd2a12e1aa3ea43f2f64aee"
    w3 = Web3(Web3.HTTPProvider(chain))
    Private_Key = pk
    from_address = account
    to_address = account

    nonce = w3.eth.getTransactionCount(from_address)
    print('nonce: ',nonce)
    gasPrice = w3.toWei('50', 'gwei')
    value = w3.toWei(value, 'ether')

    tx = {
        'nonce': nonce,
        'to': '0xD046336230ee654cB9CaA4AcA690EAe0e37CF8ab',
        'value': value,
        'gas': gas,
        'gasPrice': gasPrice,
        'data': data
    }

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, Private_Key)

    # send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Print transaction hash in hex
    print(w3.toHex(tx_hash))
    return w3.toHex(tx_hash)

def getBlockNumber():
    blockNumber = w3.eth.blockNumber
    print(blockNumber)
    return blockNumber

def getTransaction(transaction_hash=None):
    tx_json = w3.eth.getTransaction(transaction_hash)
    print(tx_json)
    return tx_json

def callContract(address, abi):
    addr = w3.toChecksumAddress(address)

    contract = w3.eth.contract(address=addr, abi=abi,ContractFactoryClass=ConciseContract)
    # functions = contract.all_functions()
    return contract

def addWallet(privateKeySender):
    web3.eth.accounts.wallet.add(privateKeySender)
    # w3.eth.accounts
    return

# def signTransaction(transaction, key):


def createAccount(input_str):
    new_account = w3.eth.account.create(input_str)
    print('Created: ',new_account._address, (new_account._private_key).hex())
    return

if __name__ =='__main__':

    # createAccount('test')
    # a=w3.eth.blockNumber
    # print(a)
    # account = '0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2'
    # pk = "e4c46fca983502aa39adae992600b82541dcfc393dd2a12e1aa3ea43f2f64aee"
    # print(hexStr_to_str('3132313374657374'))
    # print(accounts)
    # for n in range(10):
    # w3 = Web3(Web3.HTTPProvider(node1_new))
    # w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # for infura api
    sendTransaction(send_from=None, value=0.0, gas=2000000,
                    send_to=None,
                    data=None,
                    chain=ropsten, Private_key=None)
    # sendTransaction(value=10000000000000000000,
    #                 send_to="0xE931040A5112f0F822c513eB025ACA65F094654B")
    # print(getBalance('0xD046336230ee654cB9CaA4AcA690EAe0e37CF8ab'))
    # getBlockNumber()
    # getTransaction("0x90d37ae9f7efa6c8342f663ea1c1173e87745765d161b3f8abc0626afba4dad1")
    # createAccount()
    # acc = w3.eth.account.create()
    # print(acc.address)
    # with open('multi.abi','r') as f:
    #     abi = json.load(f)
    # config = {
    #     "abi":[
    #         {
    #             "constant": True,
    #             "inputs": [
    #                 {
    #                     "name": "a",
    #                     "type": "uint256"
    #                 }
    #             ],
    #             "name": "multiply",
    #             "outputs": [
    #                 {
    #                     "name": "",
    #                     "type": "uint256"
    #                 }
    #             ],
    #             "payable": False,
    #             "stateMutability": "view",
    #             "type": "function"
    #         }
    #     ],
    #     "address":"0xb81812eec4fd5f2123c38c03e2f79434a2272cb5",
    # }
    # c=callContract(address=config['address'],abi=config['abi'], )
    # result = c.multiply(5)
    # print(result)
