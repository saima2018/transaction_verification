# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/11/26 10:13
# @Author : masai
# @Email : sai.ma@spacexwalk.com
# @File : merkle_tree.py
# @Software: PyCharm

from typing import List
import typing
import hashlib

# create a node (leaf) class
class Node:
    def __init__(self, left, right, value:str, content)->None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.content = content

    @staticmethod
    def hash(val:str)->str:
        return hashlib.sha256(val.encode("utf-8")).hexdigest()
    def __str__(self):
        return(str(self.value))

# create a merkle tree class
class MerkleTree:
    def __init__(self, values: List[str])->None:
        self.__buildTree(values)
    def __buildTree(self, values: List[str])->None:
        leaves: List[Node] = [Node(None, None, Node.hash(value), value)
                              for value in values]
        if len(leaves)%2==1:
            leaves.append(leaves[-1:][0]) # duplicate the last element if odd total
        self.root: Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes:List[Node])->Node:
        half: int = len(nodes)//2
        print(half)
        if len(nodes) == 2:
            return Node(nodes[0], nodes[1], Node.hash(nodes[0].value+nodes[1].value),
                        nodes[0].content+'+'+nodes[1].content)

        left: Node = self.__buildTreeRec(nodes[:half])
        right: Node = self.__buildTreeRec(nodes[half:])
        value: str = Node.hash(left.value+right.value)
        content: str = left.content+'+'+right.content
        return Node(left, right, value, content)

    def printTree(self)->None:
        self.__printTreeRec(self.root)
    def __printTreeRec(self, node)->None:
        if node != None:
            if node.left != None:
                print('Left: '+str(node.left))
                print('Right: '+str(node.right))
            else:
                print('Original Input: ')
            print('Value: '+str(node.value))
            print('Content: '+str(node.content))
            print('')
            self.__printTreeRec(node.left)
            self.__printTreeRec(node.right)

    def getRootHash(self)->str:
        return self.root.value

def mixmerkletree()->None:
    elems = ['mix','34','4','34','mix','34','4',]
    print('Inputs: ')
    print(*elems, sep='|')
    mtree = MerkleTree(elems)
    print('Root hash: '+mtree.getRootHash()+'\n')
    print('Whole tree', mtree.printTree())



if __name__ =='__main__':
    mixmerkletree()