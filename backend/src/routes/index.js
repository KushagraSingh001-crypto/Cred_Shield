import { Router } from 'express';
import analysisRouter from './analysis.routes.js';
import blockchainRouter from './blockchain.routes.js';

const router = Router();

router.use('/analysis', analysisRouter);
router.use('/blockchain', blockchainRouter);

export default router;