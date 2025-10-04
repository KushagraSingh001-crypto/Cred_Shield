import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Upload, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { analysisAPI } from "@/lib/api";

const Dashboard = () => {
  const navigate = useNavigate();
  const [analysisMode, setAnalysisMode] = useState<'text' | 'file'>('text');
  const [textContent, setTextContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setTextContent(''); // Clear text when file is selected
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTextContent(e.target.value);
    setSelectedFile(null); // Clear file when text is entered
  };

  const handleAnalyze = async () => {
    if (!textContent && !selectedFile) {
      toast.error("Please provide content to analyze");
      return;
    }

    setIsAnalyzing(true);
    
    try {
      let response;
      
      if (selectedFile) {
        response = await analysisAPI.analyzeFile(selectedFile);
      } else {
        response = await analysisAPI.analyzeText(textContent);
      }

      if (response.success && response.data._id) {
        toast.success("Analysis complete!");
        navigate(`/results/${response.data._id}`);
      }
    } catch (error: any) {
      console.error("Analysis error:", error);
      toast.error(error.response?.data?.message || "Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-hero py-12 px-4">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            AI Content <span className="gradient-text">Analysis</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Detect AI-generated misinformation and analyze threat profiles
          </p>
        </div>

        <Card className="bg-card/80 backdrop-blur-sm border-primary/20 shadow-2xl animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-6 h-6 text-primary" />
              Content Analysis
            </CardTitle>
            <CardDescription>
              Choose your analysis method: paste text or upload a file
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Mode Selection */}
            <div className="flex gap-4">
              <Button
                variant={analysisMode === 'text' ? 'default' : 'outline'}
                onClick={() => setAnalysisMode('text')}
                className="flex-1"
              >
                <FileText className="w-4 h-4 mr-2" />
                Text Analysis
              </Button>
              <Button
                variant={analysisMode === 'file' ? 'default' : 'outline'}
                onClick={() => setAnalysisMode('file')}
                className="flex-1"
              >
                <Upload className="w-4 h-4 mr-2" />
                File Upload
              </Button>
            </div>

            {/* Text Input */}
            {analysisMode === 'text' && (
              <div className="space-y-2">
                <Label htmlFor="text-content">Text Content</Label>
                <Textarea
                  id="text-content"
                  placeholder="Paste the content you want to analyze here..."
                  value={textContent}
                  onChange={handleTextChange}
                  className="min-h-[300px] bg-background/50 border-primary/20 focus:border-primary"
                  disabled={isAnalyzing}
                />
              </div>
            )}

            {/* File Upload */}
            {analysisMode === 'file' && (
              <div className="space-y-2">
                <Label htmlFor="file-upload">Upload File</Label>
                <div className="border-2 border-dashed border-primary/20 rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
                  <Input
                    id="file-upload"
                    type="file"
                    onChange={handleFileChange}
                    className="hidden"
                    accept="image/*,video/*"
                    disabled={isAnalyzing}
                  />
                  <label 
                    htmlFor="file-upload" 
                    className="cursor-pointer flex flex-col items-center gap-2"
                  >
                    <Upload className="w-12 h-12 text-primary/50" />
                    <div>
                      <p className="text-foreground font-medium">
                        {selectedFile ? selectedFile.name : "Click to upload or drag and drop"}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Supports images and videos
                      </p>
                    </div>
                  </label>
                </div>
              </div>
            )}

            {/* Analysis Info */}
            <div className="flex items-start gap-3 p-4 bg-primary/10 border border-primary/20 rounded-lg">
              <AlertCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-medium text-foreground mb-1">How it works</p>
                <p className="text-muted-foreground">
                  Our AI analyzes your content for signs of machine-generated text, identifies 
                  threat keywords and patterns, and provides a comprehensive threat profile.
                </p>
              </div>
            </div>

            {/* Analyze Button */}
            <Button
              variant="glow"
              size="lg"
              onClick={handleAnalyze}
              disabled={isAnalyzing || (!textContent && !selectedFile)}
              className="w-full text-lg h-14"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing Content...
                </>
              ) : (
                <>
                  Analyze Content
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
