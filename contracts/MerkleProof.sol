pragma solidity ^0.7.6;

contract MerkleProof {
    function verify(
        bytes32[] memory proof, bytes32 root, uint index, address addr,
        uint balance
    )
        public pure returns (bool)
    {
        // bytes32 hash = leaf;
        bytes32 hash = keccak256(abi.encodePacked(addr, balance));

        for (uint i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];

            if (index % 2 == 0) {
                hash = keccak256(abi.encodePacked(hash, proofElement));
            } else {
                hash = keccak256(abi.encodePacked(proofElement, hash));
            }

            index = index / 2;
            h = hash;
        }

        return hash == root;
    }
}
