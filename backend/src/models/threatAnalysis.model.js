import mongoose from 'mongoose';

const threatAnalysisSchema = new mongoose.Schema({
  inputType: { type: String, enum: ['text', 'file'], required: true },
  originalContent: { type: String, required: true }, 
  aiDetectionScore: { type: Number, required: true },
  threatEntities: { type: [Object], default: [] },
  threatGraph: { type: Object, default: {} },
  isSharedOnChain: { type: Boolean, default: false },
  blockchainTransactionId: { type: String, default: null },
}, { timestamps: true });

export const ThreatAnalysis = mongoose.model("ThreatAnalysis", threatAnalysisSchema);