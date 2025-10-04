import httpClient from '../utils/httpClient.js';
import { ANALYSIS_SERVICE_URL } from '../config/services.js';

export const callAnalysisService = async (text) => {
  const response = await httpClient.post(ANALYSIS_SERVICE_URL, { text });
  return response.data;
};