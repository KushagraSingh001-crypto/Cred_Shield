import { v2 as cloudinary } from 'cloudinary';
import fs from 'fs';
import { CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET } from './index.js';

// Configure Cloudinary with credentials
cloudinary.config({
  cloud_name: CLOUDINARY_CLOUD_NAME,
  api_key: CLOUDINARY_API_KEY,
  api_secret: CLOUDINARY_API_SECRET
});

/**
 * Uploads a file from a local path to Cloudinary
 * @param {string} localFilePath - The path of the file to upload
 * @returns {object | null} The Cloudinary response object or null on failure
 */
const uploadOnCloudinary = async (localFilePath) => {
  try {
    if (!localFilePath) return null;

    const response = await cloudinary.uploader.upload(localFilePath, {
      resource_type: "auto" // Automatically detect file type (image, video, etc.)
    });

    // Remove the temporary local file after successful upload
    fs.unlinkSync(localFilePath);
    return response;

  } catch (error) {
    // Remove the temporary local file even if the upload failed
    if (fs.existsSync(localFilePath)) {
      fs.unlinkSync(localFilePath);
    }
    console.error("Cloudinary upload failed:", error);
    return null;
  }
};

export { uploadOnCloudinary };