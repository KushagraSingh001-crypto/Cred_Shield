import { Router } from 'express';
import { analyzeText, analyzeFile } from '../controllers/analysis.controller.js';
import { upload } from '../middlewares/multer.middleware.js';
import { validateTextAnalysis } from '../middlewares/validator.js';

const router = Router();

router.route('/text').post(validateTextAnalysis, analyzeText);
router.route('/file').post(upload.single('analysisFile'), analyzeFile);

export default router;