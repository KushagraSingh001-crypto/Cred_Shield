import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Shield, Database, ArrowLeft, Loader2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { analysisAPI, blockchainAPI, ThreatEntity } from "@/lib/api";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Results = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [sharing, setSharing] = useState(false);
  const [aiScore, setAiScore] = useState(0);
  const [threatEntities, setThreatEntities] = useState<ThreatEntity[]>([]);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!analysisId) {
        toast.error("No analysis ID provided");
        navigate("/dashboard");
        return;
      }

      try {
        const response = await analysisAPI.getAnalysisById(analysisId);
        
        if (response.success) {
          setAiScore(response.data.aiDetectionScore);
          setThreatEntities(response.data.threatEntities || []);
        }
      } catch (error: any) {
        console.error("Error fetching analysis:", error);
        toast.error("Failed to load analysis results");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [analysisId, navigate]);

  const handleShareToBlockchain = async () => {
    if (!analysisId) return;

    setSharing(true);
    try {
      const response = await blockchainAPI.shareToBlockchain(analysisId);
      
      if (response.success) {
        toast.success(
          `Successfully shared to blockchain! Transaction: ${response.data.transactionHash.substring(0, 10)}...`
        );
      }
    } catch (error: any) {
      console.error("Blockchain sharing error:", error);
      toast.error("Failed to share to blockchain");
    } finally {
      setSharing(false);
    }
  };

  const getThreatLevel = (score: number) => {
    if (score >= 0.8) return { level: "Critical", color: "text-destructive" };
    if (score >= 0.6) return { level: "High", color: "text-orange-500" };
    if (score >= 0.4) return { level: "Medium", color: "text-yellow-500" };
    return { level: "Low", color: "text-success" };
  };

  const chartData = {
    labels: threatEntities.map(entity => entity.name),
    datasets: [
      {
        label: 'Threat Occurrences',
        data: threatEntities.map(entity => entity.count),
        backgroundColor: 'rgba(34, 211, 238, 0.8)',
        borderColor: 'rgba(34, 211, 238, 1)',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-hero flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-xl text-muted-foreground">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  const threat = getThreatLevel(aiScore);

  return (
    <div className="min-h-screen bg-gradient-hero py-12 px-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <Button
            variant="ghost"
            onClick={() => navigate("/dashboard")}
            className="mb-4 hover:bg-primary/10"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-2">
            Analysis <span className="gradient-text">Results</span>
          </h1>
          <p className="text-muted-foreground">Analysis ID: {analysisId}</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* AI Detection Score */}
          <Card className="bg-card/80 backdrop-blur-sm border-primary/20 shadow-2xl animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-6 h-6 text-primary" />
                AI Detection Score
              </CardTitle>
              <CardDescription>
                Probability of AI-generated content
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <div className="text-7xl font-bold gradient-text mb-4">
                  {(aiScore * 100).toFixed(1)}%
                </div>
                <div className="flex items-center justify-center gap-2">
                  <AlertTriangle className={`w-5 h-5 ${threat.color}`} />
                  <span className={`text-lg font-semibold ${threat.color}`}>
                    {threat.level} Threat
                  </span>
                </div>
              </div>
              
              <Progress 
                value={aiScore * 100} 
                className="h-4"
              />
              
              <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  This score indicates the likelihood that the analyzed content was generated 
                  by artificial intelligence. Higher scores suggest stronger evidence of AI involvement.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Threat Entities Chart */}
          <Card className="bg-card/80 backdrop-blur-sm border-primary/20 shadow-2xl animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-6 h-6 text-secondary" />
                Threat Profile
              </CardTitle>
              <CardDescription>
                Key threat indicators detected in content
              </CardDescription>
            </CardHeader>
            <CardContent>
              {threatEntities.length > 0 ? (
                <div style={{ height: '300px' }}>
                  <Bar data={chartData} options={chartOptions} />
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  No threat entities detected
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Blockchain Sharing */}
        <Card className="mt-6 bg-card/80 backdrop-blur-sm border-primary/20 shadow-2xl animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <CardHeader>
            <CardTitle>Share Intelligence</CardTitle>
            <CardDescription>
              Securely share this threat intelligence on the blockchain
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">
                  By sharing this analysis to the blockchain, you contribute to a decentralized 
                  database of verified threat intelligence, helping protect others from similar content.
                </p>
              </div>
              <Button
                variant="glow"
                size="lg"
                onClick={handleShareToBlockchain}
                disabled={sharing}
                className="whitespace-nowrap"
              >
                {sharing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sharing...
                  </>
                ) : (
                  <>
                    <Database className="mr-2 h-4 w-4" />
                    Share to Blockchain
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Results;
