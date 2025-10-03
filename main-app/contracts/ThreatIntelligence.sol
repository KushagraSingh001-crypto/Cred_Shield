// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ThreatIntelligence {
    struct Threat {
        string text;            // Raw text (no hashing)
        string entities;        // JSON string of extracted entities
        uint256 timestamp;      // When threat was logged
        address submitter;      // Who submitted the threat
    }

    Threat[] public threats;
    
    event ThreatLogged(
        uint256 indexed threatId,
        string text,
        address indexed submitter,
        uint256 timestamp
    );

    function logThreat(string memory _text, string memory _entities) public {
        threats.push(Threat({
            text: _text,
            entities: _entities,
            timestamp: block.timestamp,
            submitter: msg.sender
        }));

        uint256 threatId = threats.length - 1;
        emit ThreatLogged(threatId, _text, msg.sender, block.timestamp);
    }

    function getThreat(uint256 _threatId) public view returns (Threat memory) {
        require(_threatId < threats.length, "Threat does not exist");
        return threats[_threatId];
    }

    function getThreatCount() public view returns (uint256) {
        return threats.length;
    }
}
