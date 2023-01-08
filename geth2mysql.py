# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/12/28 17:22
# @Author : masai
# @Email : sai.ma@spacexwalk.com
# @File : geth2mysql.py
# @Software: PyCharm

# !/usr/bin/env python3
import traceback

from web3 import Web3
import pymysql
import asyncio
from threading import Thread
import time
import uuid, binascii
from web3_py import *
import datetime

block = None
blockToSync = 0
batchtran = 100
latestSyncedBlock = 0
initialTran = 0
latestSynceTran = 0
import sys


# update account balance in mysql db
def updateAccountBalance(account, balance=None):
    if account in [None,'None',0,'0x']: # case when to None address for contract deployment

        return
    account_ = Web3.toChecksumAddress(account)
    balance = getBalance(account_)
    print('acccccccccc',account_, balance)
    # print(balance,account)

    # # check if address already in db
    # sql = "select 1 from account where account_address = '{}'".format(account_)
    # try:
    #     cur.execute(sql)
    # except pymysql.Error as e:
    #     print(str(e))
    # row = cur.fetchone()
    ts = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')

    # if not row:
    sql = """INSERT INTO account (account_address, balance, last_update) VALUES ('{}',{},
    STR_TO_DATE('{}', '%Y-%m-%d %H:%i:%s'))""".format(account_, str(balance),ts)
    try:
        cur.execute(sql)
        conn.commit()
    except pymysql.Error as e:
        print(str(e))
    # else:
    #     sql = """update account a set a.balance = {}, a.last_update = STR_TO_DATE('{}', '%Y-%m-%d %H:%i:%s')
    #             where a.account_address = '{}'""".format(str(balance), ts, str(account_))
    #     try:
    #         cur.execute(sql)
    #         conn.commit()
    #     except pymysql.Error as e:
    #         print(str(e))

def synctran(start, end):
    start = start + 1
    sql = "update address r set inputcount=inputcount + c.receivesum,outputcount=outputcount + c.sendsum from ( select distinct COALESCE(a.id,b.id) as addr,COALESCE(b.sendsum,0) as sendsum,COALESCE(a.receivesum,0) as receivesum  from ( select receiver as id,count(transaction.id) as receivesum from transaction  join address  on address.address=transaction.receiver  where address.balance<>'0' and transaction.id between " + str(
        start) + " and " + str(
        end) + " group by receiver ) as  a full  join  ( select sender as id,count(transaction.id) as sendsum from transaction  join address  on address.address=transaction.sender  where address.balance<>'0' and  transaction.id between " + str(
        start) + " and " + str(end) + " group by sender ) as  b on a.id=b.id ) as c WHERE r.address=c.addr "
    try:
        cur.execute(sql)
    except pymysql.Error as e:
        print(str(e))


def execquery(sql,):
    try:
        cur.execute(sql)
        conn.commit()
    except pymysql.Error as e:
        print(str(e))


def addresscounter():
    cur2 = conn.cursor()
    sql = "select address from address where balance <>'0'"
    try:
        cur2.execute(sql)
    except pymysql.Error as e:
        print(str(e))
    row = cur2.fetchone()
    while row:
        sql = "UPDATE address SET inputcount = (SELECT COUNT(*) FROM transaction WHERE receiver = '" + row[
            0] + "') WHERE address = '" + row[0] + "' "
        execquery(str(sql))
        sql = "UPDATE address SET outputcount = (SELECT COUNT(*) FROM transaction WHERE sender = '" + row[
            0] + "') WHERE address = '" + row[0] + "' "
        execquery(str(sql))
        row = cur2.fetchone()


def updateAddress(address, fromtr):
    print("checking address")
    print(address)

    if (fromtr):
        sql = "INSERT INTO address (address,inputcount,outputcount) VALUES ('" + str(
            address) + "',0,1)"
    else:
        sql = "INSERT INTO address (address,inputcount,outputcount) VALUES ('" + str(
            address) + "',1,0) "
    execquery(str(sql))
    # update account balance database
    updateAccountBalance(address)


def syncTransactions(ofblock, block, timestamp):
    global latestSyncedBlock
    global initialTran
    global latestSyncedTran
    for i in range(0, len(block.transactions)):
        tx = block.transactions[i]
        # print('fetched new tx',type(tx),tx)

        # process possible empty input or receiver
        if tx.input in ['0x', None]:
            tx_input = 0
        else:
            tx_input = tx.input
        if tx['to'] in ['0x', None]:
            tx_to = 0
        else:
            tx_to = tx['to']
        ts = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        sql = """INSERT INTO transaction (transaction_hash, value, gas, gasprice, nonce, 
        txdata, block_id,sender,receiver,timestamp) VALUES (
        hex({}),{},{},{},{},hex({}),{},hex({}),hex({}),
        STR_TO_DATE('{}', '%Y-%m-%d %H:%i:%s'))""".format(
            web3.toHex(tx.hash), str(tx.value), str(tx.gas),
            str(tx.gasPrice), str(tx.nonce), str(tx_input), str(ofblock),
            str(tx["from"]), str(tx_to),ts
        )
        execquery(str(sql))
        updateAddress(str(tx["from"]), True)
        updateAddress(str(tx.to), False)



def syncBlock(block,):
    global latestSyncedBlock
    global initialTran
    global latestSyncedTran
    if (not block):
        blockToSync = latestSyncedBlock + 1
        block = web3.eth.getBlock(blockToSync, True)
    else:
        blockToSync = block
        block = web3.eth.getBlock(blockToSync, True)
        # print('333333333',block)
    if block != None:
        ts = datetime.datetime.fromtimestamp(int(block.timestamp)).strftime('%Y-%m-%d %H:%M:%S')

        sql = """INSERT INTO block (id, blockhash, miner, timestamp, size, 
        transactions, number,uncle_hash, data, gasused) VALUES ({},
        hex({}),hex({}),STR_TO_DATE('{}', '%Y-%m-%d %H:%i:%s'),
        {},{},{},{},hex({}),{})""".format(
            str(block.number), str(web3.toHex(block.hash)), str(block.miner),
            ts, str(block.size), str(len(block.transactions)) ,
            str(block.number),'0',
            str(web3.toHex(block.extraData)), str(block.gasUsed))
        print("syncing block number " + str(blockToSync))
        print("got n: " + str(len(block.transactions)) + " transactions")

        # only sync block tx if not empty block
        if len(block.transactions) > 0:
            execquery(str(sql))
            syncTransactions(blockToSync, block, block.timestamp)
            # print(str(block.hash))
            print('current block #' + str(block.number))


def log_loop(event_filter, poll_interval):
    while True:
        try:
            for event in event_filter.get_new_entries():
                block = web3.eth.getBlock(event)
                print("new block:", block.number)
                syncBlock(block.number)
        except:
            print(traceback.print_exc())

def synced():
    global initialTran
    global latestSyncedTran
    print("SYNCED")
    block_filter = web3.eth.filter('latest')
    print('block filter 00000000', block_filter)
    log_loop(block_filter, 5)


def main():
    global block
    global latestSyncedBlock
    global initialTran
    global latestSyncedTran
    global latestBlock
    conn.ping(reconnect=True)
    cur.execute("SELECT max(id) as total FROM block  ")
    result = cur.fetchone()
    print('latestSyncedBlock block fetched from database:', result[0])
    latestSyncedBlock = int(result[0])
    latestBlock = web3.eth.blockNumber # newest block from blockchain
    while (latestSyncedBlock < latestBlock):
        print('Latest block:', latestBlock)
        if (latestSyncedBlock == latestBlock):
            latestBlock = web3.eth.blockNumber # newest block from blockchain after syncs
        latestSyncedBlock = latestSyncedBlock + 1
        syncBlock(latestSyncedBlock)

        #
        latestBlock = web3.eth.blockNumber
        while latestSyncedBlock >= latestBlock:
            # wait for the chain to generate new blocks
            # print('waiting for the chain to generate new blocks')
            time.sleep(10)
            latestBlock = web3.eth.blockNumber
    # synced()


if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    conn = pymysql.connect(db='geth_private2022', user='root', password='some34QA!',host='192.168.1.111', port=3306, )
    cur = conn.cursor()
    ropsten = 'https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'
    node1 = "http://192.168.1.111:8899"
    node1_new = "https://chain.planckx.io/"
    web3 = Web3(Web3.HTTPProvider(node1_new))
    main()
    # updateAccountBalance('0xD046336230ee654cB9CaA4AcA690EAe0e37CF8ab')