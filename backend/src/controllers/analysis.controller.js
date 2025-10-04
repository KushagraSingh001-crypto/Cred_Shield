import { asyncHandler } from '../utils/asyncHandler.js';
import { ApiError } from '../utils/ApiError.js';
import { ApiResponse } from '../utils/apiResponse.js';
import { uploadOnCloudinary } from '../config/cloudinary.js';
import { ThreatAnalysis } from '../models/threatAnalysis.model.js';
import { orchestrateTextAnalysis, orchestrateMediaAnalysis } from '../services/orchestrator.js';

/**
 * @desc    Orchestrates a full analysis of a given text, saves the result, and returns it.
 * @route   POST /api/v1/analysis/text
 * @access  Public
 */
export const analyzeText = asyncHandler(async (req, res) => {
    const { text } = req.body;
    let analysisResult;

    // --- Step 1: Call Orchestrator Service ---
    try {
        analysisResult = await orchestrateTextAnalysis(text);
    } catch (error) {
        console.error(`Orchestration Error for text analysis: ${error.message}`);
        throw new ApiError(502, "One or more analysis services are unavailable.");
    }

    // --- Step 2: Save Results to Database ---
    try {
        const dbPayload = {
            inputType: 'text',
            originalContent: text,
            ...analysisResult
        };
        const newAnalysis = await ThreatAnalysis.create(dbPayload);

        // Use 201 Created for successfully creating a new resource.
        return res
            .status(201)
            .json(new ApiResponse(201, newAnalysis, "Text analysis completed and recorded successfully."));
    } catch (error) {
        console.error(`Database Error: Failed to save text analysis result. Reason: ${error.message}`);
        throw new ApiError(500, "Failed to save analysis results due to a server error.");
    }
});


/**
 * @desc    Orchestrates a full analysis of an uploaded file, saves the result, and returns it.
 * @route   POST /api/v1/analysis/file
 * @access  Public
 */
export const analyzeFile = asyncHandler(async (req, res) => {
    // --- Step 1: Validate and Handle File Upload ---
    if (!req.file || !req.file.path) {
        throw new ApiError(400, "An analysis file is required. Please upload a file.");
    }
    
    let cloudinaryFile;
    try {
        cloudinaryFile = await uploadOnCloudinary(req.file.path);
        if (!cloudinaryFile || !cloudinaryFile.url) {
            // This specifically handles failures in the upload-to-cloudinary step.
            throw new Error("Cloudinary upload returned no URL.");
        }
    } catch (error) {
        console.error(`File Upload Error: Failed to upload to Cloudinary. Reason: ${error.message}`);
        throw new ApiError(500, "Failed to process the file upload.");
    }

    // --- Step 2: Call Media Orchestrator Service ---
    let analysisResult;
    try {
        analysisResult = await orchestrateMediaAnalysis(cloudinaryFile.url);
    } catch (error) {
        console.error(`Orchestration Error for file analysis: ${error.message}`);
        throw new ApiError(502, "The media analysis service is currently unavailable.");
    }

    // --- Step 3: Save Results to Database ---
    try {
        const dbPayload = {
            inputType: 'file',
            originalContent: cloudinaryFile.url,
            ...analysisResult
        };
        const newAnalysis = await ThreatAnalysis.create(dbPayload);

        // Respond with 201 Created and the newly created document.
        return res
            .status(201)
            .json(new ApiResponse(201, newAnalysis, "File analysis completed and recorded successfully."));
    } catch (error) {
        console.error(`Database Error: Failed to save file analysis result. Reason: ${error.message}`);
        throw new ApiError(500, "Failed to save analysis results due to a server error.");
    }
});