import express from 'express';
import cors from 'cors';
import mainRouter from './routes/index.js';
import { errorHandler } from './middlewares/errorHandler.js';
import requestLogger from './middlewares/logger.js';
import { CORS_ORIGIN } from './config/index.js';

const app = express();

// --- Global Middleware ---

// Enable Cross-Origin Resource Sharing (CORS)
app.use(cors({
  origin: CORS_ORIGIN,
  credentials: true
}));

// Parse incoming JSON requests with a size limit
app.use(express.json({ limit: '16kb' }));

// Parse incoming URL-encoded requests
app.use(express.urlencoded({ extended: true, limit: '16kb' }));

// Serve static files from the "public" directory
app.use(express.static('public'));

// Use the custom request logger
app.use(requestLogger);

// --- API Routes ---
// All routes will be prefixed with /api/v1
app.use('/api/v1', mainRouter);

// --- Global Error Handler ---
// This middleware will catch all errors passed by next()
app.use(errorHandler);

export { app };