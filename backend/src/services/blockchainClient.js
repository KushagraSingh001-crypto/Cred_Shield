import httpClient from '../utils/httpClient.js';
import { BLOCKCHAIN_SERVICE_URL } from '../config/services.js';

export const callBlockchainService = async (payload) => {
  const response = await httpClient.post(BLOCKCHAIN_SERVICE_URL, payload);
  return response.data;
};