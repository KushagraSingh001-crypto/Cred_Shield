import { useNavigate } from "react-router-dom";
import { Shield, Zap, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import heroBg from "@/assets/hero-bg.jpg";

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section 
        className="relative min-h-screen flex items-center justify-center overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(rgba(20, 25, 45, 0.9), rgba(20, 25, 45, 0.95)), url(${heroBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-hero opacity-50"></div>
        
        <div className="container mx-auto px-4 z-10">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 bg-card/50 border border-primary/30 rounded-full backdrop-blur-sm">
              <Shield className="w-4 h-4 text-primary" />
              <span className="text-sm text-muted-foreground">AI-Powered Threat Detection</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
              Unmasking Digital{" "}
              <span className="gradient-text">Deception</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-2xl mx-auto">
              Advanced AI detection technology to identify misinformation, analyze threat profiles, 
              and secure intelligence on the blockchain. Protect your organization from digital deception.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                variant="hero" 
                size="lg"
                onClick={() => navigate("/dashboard")}
                className="text-lg px-8 py-6 h-auto"
              >
                Get Started
                <Zap className="ml-2 w-5 h-5" />
              </Button>
              
              <Button 
                variant="outline" 
                size="lg"
                className="text-lg px-8 py-6 h-auto border-primary/50 hover:bg-primary/10"
              >
                Learn More
              </Button>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-primary/20 rounded-full blur-xl animate-float"></div>
        <div className="absolute bottom-20 right-10 w-32 h-32 bg-secondary/20 rounded-full blur-xl animate-float" style={{ animationDelay: '2s' }}></div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-card/30">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">
            Powered by <span className="gradient-text">Advanced AI</span>
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <Card className="bg-card/50 border-primary/20 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:glow-primary">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">AI Detection</h3>
                <p className="text-muted-foreground">
                  State-of-the-art machine learning algorithms detect AI-generated content with unprecedented accuracy.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card/50 border-primary/20 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:glow-primary">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-secondary/20 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-secondary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">Threat Analysis</h3>
                <p className="text-muted-foreground">
                  Comprehensive threat profiling identifies keywords, topics, and patterns in suspicious content.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card/50 border-primary/20 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 hover:glow-primary">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mb-4">
                  <Database className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">Blockchain Security</h3>
                <p className="text-muted-foreground">
                  Share intelligence securely on the blockchain, ensuring immutable and transparent threat reporting.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Landing;
