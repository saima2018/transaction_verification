# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/11/26 14:48
# @Author : masai
# @Email : sai.ma@spacexwalk.com
# @File : merkle.py
# @Software: PyCharm
import datetime
import json
import traceback
import time
import math
import pymysql
import os
from web3 import Web3
from flask import Flask, request
from multiprocessing import Process, Value
app = Flask(__name__)


class Merkleroot(object):
    def __init__(self):
        self.height = 1
        self.whole_tree = {}

    def createLeafHash(self, transactions):
        ##compute a list of hashes from transactions
        leafHash = []
        for trans in transactions:
            # leafHash.append(doubleSha256(trans))
            leafHash.append(solidityHash(['address','uint256'],[trans[0],int(trans[1])]))
        self.whole_tree[1] = leafHash # 第一层是交易信息的哈希，而非实际交易信息

        return leafHash

    def findMerkleRoot(self, leafHash):

        self.height += 1
        hash = []
        hash2 = []

        if len(leafHash) % 2 != 0:  ##if not even, repeat the last element
            leafHash.extend(leafHash[-1:])

        for leaf in leafHash:  ##for each leaf
            hash.append(leaf)
            if len(hash) % 2 == 0:  ##only add secondary hash if there are two first hash
                # hash2.append(doubleSha256(hash[0] + hash[1]))  ##run through hash func for both hashes
                hash2.append(solidityHash(['bytes'],[hash[0]+hash[1]]))
                hash = []  ##reset first hash to empty
        if len(hash2) == 1:  ##if secondary hash is only one, we are the root
            self.whole_tree[self.height] = hash2
            return hash2
        else:
            # print(len(hash2), hash2,'\n')
            self.whole_tree[self.height] = hash2
            return self.findMerkleRoot(hash2)  ##if not, recurse with hash2


# return hash path for verification of a particular tx_number
def getPath2root(tx_number, merkle_tree, tx_hash): # index starts at 1 not 0
    original_idx = tx_number
    tree_height = len(merkle_tree)
    if (tx_number > len(merkle_tree[1])) or (tx_number < 1):
        return 'Transaction index invalid'
    hash_path = [] # to store the hashes needed to calculate the root
    hash_path.append(merkle_tree[1][tx_number-1])
    for level in range(1,tree_height):
        # print(tx_number)
        if tx_number % 2 == 0:
            hash_number_for_current_level = int(tx_number-1)
            hash_for_current_level = merkle_tree[level][hash_number_for_current_level-1]
            hash_path.append(hash_for_current_level)
            tx_number = int(tx_number / 2)
        else:
            hash_number_for_current_level = int(tx_number+1)
            hash_for_current_level = merkle_tree[level][hash_number_for_current_level-1]
            hash_path.append(hash_for_current_level)
            tx_number = math.ceil(hash_number_for_current_level/2)
        # print('hhh',hash_number_for_current_level)
    # append root as the last hash
    hash_path.append(merkle_tree[tree_height][0])
    hash_path_output = []
    for hash in hash_path:
        # hash_path_output.append('0x'+str(hash.hex()))
        hash_path_output.append(hash)
    # print('000000000,', hash_path_output[-1],type(hash_path_output[-1]))
    # print('hash_path output',hash_path_output)
    return json.dumps({#'leaf': hash_path_output[0],
            'transaction hash': str(hex(int(tx_hash))),
            'proof': hash_path_output[1:-1],
            'index': original_idx,
            'root': hash_path_output[-1]})

def solidityHash(input_type, input):
    output = Web3.solidityKeccak(input_type,input)
    return bytes(output)


def getBalanceDB(account:str):
    conn = pymysql.connect(db='geth_private2022', user='root', password='some34QA!', host='192.168.1.111', port=3306, )
    cur = conn.cursor()
    # account format check
    if len(account) != 42:
        print('Account invalid')
        return None
    account_ = Web3.toChecksumAddress(account)

    sql = """SELECT balance from account where account_address = '{}'""".format(account)
    try:
        cur.execute(sql)
    except pymysql.Error as e:
        print(str(e))
    balance = cur.fetchone()[0]
    conn.close()
    print(account_, balance)
    return balance

def sendTransaction(data=None):
    account = '0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2'
    pk = "e4c46fca983502aa39adae992600b82541dcfc393dd2a12e1aa3ea43f2f64aee"
    ropsten = 'https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'
    w3 = Web3(Web3.HTTPProvider(ropsten))
    Private_Key = pk
    from_address = account
    nonce = w3.eth.getTransactionCount(from_address)
    print('nonce: ',nonce)
    gasPrice = w3.toWei('50', 'gwei')
    value = w3.toWei(0.0, 'ether')
    tx = {
        'nonce': nonce,
        'to': account,
        'value': value,
        'gas': 2000000,
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

# create and store a merkle tree txt file for the transactions between
# start and end ids
def storeMerkleTree():
    conn1 = pymysql.connect(db='geth_private2022', user='root', password='some34QA!', host='192.168.1.111', port=3306, )
    cur1 = conn1.cursor()
    cur1.execute("SELECT max(id) FROM account")
    end = cur1.fetchone()[0] # get id of latest tx synced in mysql
    # read the previous end id and += 1 to get the current start id
    with open('../tree_files/start_id/start_id.txt', 'r+') as f:
        start = f.read() # id of last processed tx in the previous cycle
        f.seek(0)
        f.truncate() # clear file data before writing
        f.write(str(end)) # write current end id as the next start
    f.close()
    if start != None:
        start = eval(start)+1
    transactions = [] # account balance pairs in fact
    print('start, end', start, end)
    sql = """SELECT id, account_address, balance from account where id <= '{}'
            and id >= '{}'""".format(end, start)
    try:
        if int(end) >= int(start):
            cur1.execute(sql)
        else:
            return
    except:
        print(traceback.print_exc())

    account_balance_pairs = cur1.fetchall()
    conn1.close()
    if len(account_balance_pairs) ==0:
        print('Fetched nothing from account table. Return.')
        return
    start_id = account_balance_pairs[0][0]
    end_id = account_balance_pairs[-1][0]
    for pair in account_balance_pairs:
        transactions.append([str(pair[1]),str(pair[2])])
    # print(transactions)
    mr = Merkleroot()
    leafHash = mr.createLeafHash(transactions)
    root = '0x'+mr.findMerkleRoot(leafHash)[0].hex()
    whole_tree = mr.whole_tree
    whole_tree_new = {}
    for k,v in whole_tree.items():
        whole_tree_new[k] = []
        for n in v:
            whole_tree_new[k].append('0x'+n.hex())

    # print(root, whole_tree_new)
    tx_hash = sendTransaction(data=root)
    print('Root recorded at: ', tx_hash)
    name = 'tree'+str(start_id)+'_'+str(end_id)
    with open('../tree_files/{}.txt'.format(name),'w') as f:
        f.write('tree root:\n'+root+'\n'+ 'whole tree:\n'+str(whole_tree_new)
                +'\ntransactions:\n'+str(transactions)+'\ntx_hash\n'+tx_hash)
    f.close()

    # store root on chain
    print('Stored proof for transactions {} to {}.'.format(start, end))


# 用户输入地址，返回证据数据。用户取得证据数据，并输入合约进行验证
@app.route('/get_proof', methods=['POST'])
def getProof():
    conn = pymysql.connect(db='geth_private2022', user='root', password='some34QA!', host='192.168.1.111', port=3306, )
    cur = conn.cursor()
    if request.method == 'POST':
        account = request.form['account']
        print('Querying proof for account: ',account)

    # 获取该账户在account表中的id，并基于该id选择file查找证据数据
    sql = """SELECT id from account where account_address = '{}' 
        order by id desc LIMIT 1""".format(account)
    try:
        cur.execute(sql)
    except:
        print(traceback.print_exc())
    result = cur.fetchone()
    print(result, type(result))
    conn.close()
    if result != None:
        id = result[0]

    else:
        return 'Account info invalid or not yet synced.'
    file_dir = '../tree_files/'
    file_list = os.listdir(file_dir)
    file = None
    for file_name in file_list:
        if file_name.endswith('.txt'):
            start = file_name[4:-4].split('_')[0]
            end = file_name[4:-4].split('_')[1]
            if id <= int(end) and id >= int(start):
                file = file_name
                break
    if file == None:
        return 'Account info not yet synced.'
    with open(os.path.join(file_dir, file), 'r') as f:
        info = f.readlines()
    f.close()
    tree = eval(info[3])
    tx_list = eval(info[5])
    tx_hash = eval(info[7])
    for n in tx_list:
        if account == n[0]:
            idx = tx_list.index(n) + 1
    print('111111',idx, tree)
    return getPath2root(idx, tree, tx_hash)

# the loop function that stores tx into txt files periodically
# and send root as tx comment data to main chain
def storeProof():
    while True:
        try:
            if datetime.datetime.now().minute % 1 == 0:
                storeMerkleTree()

                time.sleep(20)
        except:
            print(traceback.print_exc())
if __name__ =='__main__':
    # transactions = [['0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2',1],['0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2',2]]
    # mr = Merkleroot()
    # leafHash = mr.createLeafHash(transactions)
    # print('leafhash:', [leaf.hex() for leaf in leafHash])
    # mr.findMerkleRoot(leafHash)
    # print('whole tree: ',mr.whole_tree)
    # b = getPath2root(1, mr.whole_tree)
    # print(b)
    # a=storeMerkleTree()
    # print(a)
    # a=getProof('0x22635217e527A7e98a3D2344552a237d5C3FCF36')
    # print(a)

    p = Process(target=storeProof, )
    p.start()
    app.run(debug=False, host='0.0.0.0',port=2306)
    p.join()


    # a=solidityHash(['address','string','uint256'],
    # ['0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2',':',1])
    # b=solidityHash(['string'],
    # ['0x899Ba0df19Bf8AF9de0A6Ccc5fE63512C7477bb2:1'])
    #
    # print(a.hex(),b.hex())