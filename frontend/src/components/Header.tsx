import { Bot, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { HealthIndicator } from './HealthIndicator';

interface HeaderProps {
  onNewSession: () => void;
  sessionId: string;
}

export function Header({ onNewSession, sessionId }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Bot className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Atlan Customer Support Copilot
              </h1>
              <p className="text-gray-600 text-sm">
                AI-powered support with intelligent classification
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-gray-500 text-xs font-mono bg-gray-100 px-2 py-1 rounded">
              Session: {sessionId.slice(-8)}
            </div>
            
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onNewSession}
              className="border-blue-200 text-blue-600 hover:bg-blue-50"
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
