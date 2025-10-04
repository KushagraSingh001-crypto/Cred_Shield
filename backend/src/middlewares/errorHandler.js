import { ApiError } from '../utils/ApiError.js';

const errorHandler = (err, req, res, next) => {
  let statusCode = err.statusCode || 500;
  let message = err.message || "Internal Server Error";

  if (!(err instanceof ApiError)) {
    console.error(err.stack); // Log the full stack for non-ApiError types
  }

  res.status(statusCode).json({
    success: false,
    message: message,
    errors: err.errors || [],
  });
};

export { errorHandler };