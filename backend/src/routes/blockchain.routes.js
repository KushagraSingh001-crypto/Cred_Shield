import { Router } from 'express';
import { shareIntelligence } from '../controllers/blockchain.controller.js';

const router = Router();

// Defines the POST route for sharing, which takes a dynamic analysisId
router.route('/share/:analysisId').post(shareIntelligence);

export default router;