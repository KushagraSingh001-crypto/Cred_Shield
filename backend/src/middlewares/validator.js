import { ApiError } from '../utils/ApiError.js';

export const validateTextAnalysis = (req, res, next) => {
  const { text } = req.body;
  if (!text || typeof text !== 'string' || text.trim() === '') {
    return next(new ApiError(400, "The 'text' field is required and must be a non-empty string."));
  }
  next();
};