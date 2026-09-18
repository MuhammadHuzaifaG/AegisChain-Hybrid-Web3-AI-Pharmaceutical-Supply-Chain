// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title Aegis Supply Chain
 * @dev Immutable ledger for tracking pharmaceutical provenance.
 */
contract SupplyChain {
    struct MedicineBatch {
        string batchId;
        string medicineName;
        address manufacturer;
        uint256 manufacturingDate;
        string dataHash; // IPFS or cryptographic hash of detailed telemetry/documents
        bool isRegistered;
    }

    struct TransitRecord {
        address handler;
        uint256 timestamp;
        string location;
        string temperatureData;
    }

    mapping(string => MedicineBatch) public batches;
    mapping(string => TransitRecord[]) public transitHistory;

    event BatchRegistered(string indexed batchId, string medicineName, address indexed manufacturer);
    event TransitUpdated(string indexed batchId, address indexed handler, string location);

    /**
     * @dev Registers a new medicine batch into the immutable ledger.
     */
    function registerBatch(
        string memory _batchId,
        string memory _medicineName,
        string memory _dataHash
    ) public {
        require(!batches[_batchId].isRegistered, "Batch ID already exists");

        batches[_batchId] = MedicineBatch({
            batchId: _batchId,
            medicineName: _medicineName,
            manufacturer: msg.sender,
            manufacturingDate: block.timestamp,
            dataHash: _dataHash,
            isRegistered: true
        });

        emit BatchRegistered(_batchId, _medicineName, msg.sender);
    }

    /**
     * @dev Updates the transit history of a specific batch.
     */
    function updateTransit(
        string memory _batchId,
        string memory _location,
        string memory _temperatureData
    ) public {
        require(batches[_batchId].isRegistered, "Batch not found");

        TransitRecord memory newRecord = TransitRecord({
            handler: msg.sender,
            timestamp: block.timestamp,
            location: _location,
            temperatureData: _temperatureData
        });

        transitHistory[_batchId].push(newRecord);
        emit TransitUpdated(_batchId, msg.sender, _location);
    }

    /**
     * @dev Retrieves the complete transit history for a batch.
     */
    function getTransitHistory(string memory _batchId) public view returns (TransitRecord[] memory) {
        require(batches[_batchId].isRegistered, "Batch not found");
        return transitHistory[_batchId];
    }
}