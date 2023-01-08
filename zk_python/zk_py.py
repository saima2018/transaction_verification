# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/11/30 16:02
# @Author : masai
# @Email : sai.ma@spacexwalk.com
# @File : zk_py.py
# @Software: PyCharm

import random
import hashlib
from math import log2, ceil

def get_witness(problem, assignment):
    sum = 0
    mx = 0
    side_obfuscator = 1 - 2*random.randint(0,1) # generate 1 or -1 randomly
    witness = [sum] # p in the case of https://zhuanlan.zhihu.com/p/128566089
    assert len(problem) == len(assignment)
    for num, side in zip(problem, assignment):
        assert side == 1 or side == -1
        sum += side * num * side_obfuscator # calculate elements in witness/p
        witness += [sum]
        mx = max(mx, num)
        print(mx)
    assert sum == 0
    shift = random.randint(0, mx)
    print(shift)
    witness = [x + shift for x in witness]
    return witness

def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

class ZkMerkleTree:
    """
    A Zero Knowledge Merkle tree implementation using SHA256
    """
    def __init__(self, data):
        self.data = data
        next_pow_of_2 = int(2**ceil(log2(len(data))))
        self.data.extend([0] * (next_pow_of_2 - len(data)))
        # Intertwine with randomness to obtain zero knowledge.
        rand_list = [random.randint(0, 1 << 32) for x in self.data]
        self.data = [x for tup in zip(self.data, rand_list) for x in tup]
        # Create bottom level of the tree (i.e. leaves).
        self.tree = ["" for x in self.data] + \
                    [hash_string(str(x)) for x in self.data]
        for i in range(len(self.data) - 1, 0, -1):
            self.tree[i] = hash_string(self.tree[i * 2] + self.tree[i * 2 + 1])

    def get_root(self):
        return self.tree[1]

    def get_val_and_path(self, id):
        # Because of the zk padding, the data is now at id * 2
        id = id * 2
        val = self.data[id]
        auth_path = []
        id = id + len(self.data)
        while id > 1:
            auth_path += [self.tree[id ^ 1]]
            id = id // 2
        return val, auth_path

def verify_zk_merkle_path(root, data_size, value_id, value, path):
    cur = hash_string(str(value))
    # Due to zk padding, data_size needs to be multiplied by 2, as does the value_id
    tree_node_id = value_id * 2 + int(2**ceil(log2(data_size * 2)))
    for sibling in path:
        assert tree_node_id > 1
        if tree_node_id % 2 == 0:
            cur = hash_string(cur + sibling)
        else:
            cur = hash_string(sibling + cur)
        tree_node_id = tree_node_id // 2
    assert tree_node_id == 1
    return root == cur

def get_proof(problem, assignment, num_queries):
    proof = []
    randomness_seed = problem[:]
    for i in range(num_queries):
        witness = get_witness(problem, assignment)
        tree = ZkMerkleTree(witness)
        random.seed(str(randomness_seed))
        query_idx = random.randint(0, len(problem))
        query_and_response = [tree.get_root()]
        query_and_response += [query_idx]
        query_and_response += tree.get_val_and_path(query_idx)
        query_and_response += tree.get_val_and_path((query_idx + 1) % len(witness))
        proof += [query_and_response]
        randomness_seed += [query_and_response]
    return proof

def verify_proof(problem, proof):
    proof_checks_out = True
    randomness_seed = problem[:]
    for query in proof:
        random.seed(str(randomness_seed))
        query_idx = random.randint(0, len(problem))
        merkle_root = query[0]
        proof_checks_out &= query_idx == query[1]
        # Test witness properties.
        if query_idx < len(problem):
            proof_checks_out &= abs(query[2] - query[4]) == abs(problem[query_idx])
        else:
            proof_checks_out &= query[2] == query[4]
        # Authenticate paths
        proof_checks_out &= \
            verify_zk_merkle_path(merkle_root, len(problem) + 1, query_idx, query[2], query[3])
        proof_checks_out &= \
            verify_zk_merkle_path(merkle_root, len(problem) + 1, \
                                 (query_idx + 1) % (len(problem) + 1), query[4], query[5])
        randomness_seed += [query]
    return proof_checks_out

def zk_test(q):
    problem = [1, 2, 3, 6, 6, 6, 12]
    assignment = [1, 1, 1, -1, -1, -1, 1]
    proof = get_proof(problem, assignment, q)
    print(proof)
    return verify_proof(problem, proof)

if __name__ =='__main__':
    # a= get_witness([2,-2,-4],[1,-1,1])
    # print(a)
    a=zk_test(10)
    print(a)