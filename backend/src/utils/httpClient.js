import axios from 'axios';

const httpClient = axios.create({
  timeout: 10000, // 10-second timeout for requests
});

export default httpClient;