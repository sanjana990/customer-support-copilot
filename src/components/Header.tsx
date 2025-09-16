import { Bot, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { HealthIndicator } from './HealthIndicator';

interface HeaderProps {
  onNewSession: () => void;
  sessionId: string;
}

export function Header({ onNewSession, sessionId }: HeaderProps) {
  return (
    <header className="bg-gradient-primary border-b border-dashboard-border shadow-soft">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">
                Atlan Customer Support Copilot
              </h1>
              <p className="text-white/80 text-sm">
                AI-powered support with intelligent classification
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-white/60 text-xs font-mono bg-white/10 px-2 py-1 rounded">
              Session: {sessionId.slice(-8)}
            </div>
            
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={onNewSession}
              className="bg-white/20 text-white hover:bg-white/30 border-white/20"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Session
            </Button>
            
            <HealthIndicator />
          </div>
        </div>
      </div>
    </header>
  );
}