# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/12/13 17:47
# @Author : masai
# @Email : sai.ma@spacexwalk.com
# @File : contract_ops.py
# @Software: PyCharm
import json
from web3 import Web3
ropsten="https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
w3 = Web3(Web3.HTTPProvider(ropsten))
# address of deployed contract
address = "0xCC8C67a57f5E8553F95aBc21e00b8a967a6c69dC"
# abi of contract compiled
abi ='[{"anonymous": false,	"inputs": [{"indexed": true,"internalType": "uint256","name": "_var","type": "uint256"}],"name": "MyEvent","type": "event"},{"inputs": [{"internalType": "uint8","name": "_var","type": "uint8"}],"name": "setVar","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "_myVar","outputs": [{"internalType": "uint8","name": "","type": "uint8"	}],	"stateMutability": "view","type": "function"},{"inputs": [],"name": "getVar","outputs": [{"internalType": "uint8","name": "","type": "uint8"}],"stateMutability": "view","type": "function"}]'
abi = json.loads(abi)
contract=w3.eth.contract(address=address,abi=abi)
vv = contract.functions.getVar().call()
print(vv)