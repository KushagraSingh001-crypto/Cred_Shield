import mongoose from 'mongoose';
import { MONGODB_URI } from './index.js';

const connectDB = async () => {
  try {
    const connectionInstance = await mongoose.connect(MONGODB_URI);
    console.log(`\n✅ MongoDB connected! DB HOST: ${connectionInstance.connection.host}`);
  } catch (error) {
    console.error("MONGODB connection error: ", error);
    process.exit(1);
  }
};

export default connectDB;