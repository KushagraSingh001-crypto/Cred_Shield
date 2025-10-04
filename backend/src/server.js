import dotenv from 'dotenv';
import connectDB from './config/db.js';
import { app } from './app.js';
import { PORT } from './config/index.js';

// Load environment variables from the .env file into process.env
dotenv.config();

// Connect to the database and then start the server
connectDB()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`✅ Server is running on port: ${PORT}`);
    });
  })
  .catch((err) => {
    console.error("MONGO DB connection failed !!! ", err);
    process.exit(1);
  });