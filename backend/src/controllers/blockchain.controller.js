import { asyncHandler } from '../utils/asyncHandler.js';
import { ApiError } from '../utils/ApiError.js';
import { ApiResponse } from '../utils/ApiResponse.js';
import { ThreatAnalysis } from '../models/threatAnalysis.model.js';
import { callBlockchainService } from '../services/blockchainClient.js';
import mongoose from 'mongoose';

/**
 * @desc    Shares threat intelligence on the blockchain via the dedicated microservice.
 * @route   POST /api/v1/blockchain/share/:analysisId
 * @access  Public
 */
export const shareIntelligence = asyncHandler(async (req, res) => {
    const { analysisId } = req.params;

    // --- Step 1: Validate Input and Find Record ---
    if (!mongoose.Types.ObjectId.isValid(analysisId)) {
        throw new ApiError(400, "Invalid Analysis ID format.");
    }
    const analysis = await ThreatAnalysis.findById(analysisId);

    if (!analysis) {
        throw new ApiError(404, "Analysis record with this ID was not found.");
    }
    if (analysis.isSharedOnChain) {
        throw new ApiError(400, "This threat intelligence has already been shared.");
    }

    // --- Step 2: Prepare the Payload for the Blockchain Service ---
    const payload = {
        text: analysis.originalContent,
        // CRITICAL CHANGE: Convert the entities array into a JSON string
        // because the smart contract's logThreat function expects a string.
        entities: JSON.stringify(analysis.threatEntities)
    };

    // --- Step 3: Call the Blockchain Service ---
    let blockchainResult;
    try {
        blockchainResult = await callBlockchainService(payload);
        if (!blockchainResult || !blockchainResult.transaction_hash) {
             throw new Error("Blockchain service returned an invalid response.");
        }
    } catch (error) {
        console.error(`Blockchain Service Error: ${error.message}`);
        throw new ApiError(502, "The blockchain intelligence sharing service is currently unavailable.");
    }

    // --- Step 4: Update Our Database Record ---
    try {
        analysis.isSharedOnChain = true;
        analysis.blockchainTransactionId = blockchainResult.transaction_hash;
        await analysis.save({ validateBeforeSave: false });
    } catch (error) {
        console.error(`Database Error: Failed to update analysis record after blockchain share. Reason: ${error.message}`);
        throw new ApiError(500, "Failed to finalize the sharing process due to a database error.");
    }
    
    return res
        .status(200)
        .json(new ApiResponse(200, { transactionHash: blockchainResult.transaction_hash }, "Threat intelligence shared and recorded successfully."));
});