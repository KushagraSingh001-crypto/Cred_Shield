import { callAnalysisService } from './analysisClient.js'; // Updated import
import axios from 'axios';

/**
 * Orchestrates a call to the unified Python analysis service.
 */
export const orchestrateTextAnalysis = async (text) => {
  try {
    // Make a single call to our new unified service
    const analysisResult = await callAnalysisService(text);

    // Map the comprehensive response to our backend's data structure
    const entities = analysisResult.keywords.map(kw => ({ name: kw.term, type: 'KEYWORD', count: kw.count }));
    const graphNodes = analysisResult.keywords.map((kw, index) => ({ id: index + 1, label: kw.term, value: kw.count }));
    const graphEdges = [];
    if (graphNodes.length > 1) {
      for (let i = 1; i < graphNodes.length; i++) {
        graphEdges.push({ from: 1, to: i + 1 });
      }
    }

    // Add toxicity info if the content is toxic
    if (analysisResult.toxicity_analysis.label === 'toxic' && analysisResult.toxicity_analysis.confidence_score > 0.7) {
        entities.unshift({
            name: 'TOXIC CONTENT',
            type: 'LABEL',
            score: analysisResult.toxicity_analysis.confidence_score
        });
    }

    return {
      aiDetectionScore: analysisResult.ai_confidence_score, // Direct mapping
      threatEntities: entities,
      threatGraph: { nodes: graphNodes, edges: graphEdges },
    };

  } catch (error) {
    console.error("Error in text analysis orchestration:", error.message);
    throw new Error("Failed to orchestrate text analysis.");
  }
};

/**
 * Calls the Sightengine API (unchanged).
 */
export const orchestrateMediaAnalysis = async (mediaUrl) => {
    // ... (This function remains exactly the same)
    console.log("✅ Calling Sightengine API for media analysis...");
    try {
        const apiKey = process.env.SIGHTENGINE_API_KEY;
        const apiSecret = process.env.SIGHTENGINE_API_SECRET;
        const response = await axios.get("https://api.sightengine.com/1.0/check.json", {
            params: { url: mediaUrl, models: "genai", api_user: apiKey, api_secret: apiSecret },
            timeout: 20000
        });
        let aiScore = 0;
        if (response.data && response.data.genai && response.data.genai.score) {
            aiScore = response.data.genai.score;
        }
        return {
            aiDetectionScore: aiScore,
            threatEntities: [],
            threatGraph: {},
        };
    } catch (error) {
        if (error.response) {
            console.error("Sightengine API Error:", error.response.data);
        } else {
            console.error("Error calling Sightengine:", error.message);
        }
        throw new Error("Failed to analyze media with Sightengine.");
    }
};