import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Header } from '@/components/Header';
import { BulkDashboard } from '@/components/BulkDashboard';
import { InteractiveAgent } from '@/components/InteractiveAgent';
import { useSession } from '@/hooks/useSession';

export default function Dashboard() {
  const { sessionId, createNewSession, clearSession } = useSession();
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleNewSession = () => {
    createNewSession();
  };

  const handleClearSession = () => {
    clearSession();
  };

  return (
    <div className="min-h-screen bg-dashboard-bg">
      <Header 
        onNewSession={handleNewSession}
        sessionId={sessionId}
      />
      
      <main className="container mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 max-w-md bg-white shadow-soft">
            <TabsTrigger 
              value="dashboard" 
              className="data-[state=active]:bg-gradient-primary data-[state=active]:text-white"
            >
              Bulk Dashboard
            </TabsTrigger>
            <TabsTrigger 
              value="agent"
              className="data-[state=active]:bg-gradient-primary data-[state=active]:text-white"
            >
              Interactive Agent
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="dashboard" className="space-y-4">
            <BulkDashboard />
          </TabsContent>
          
          <TabsContent value="agent" className="space-y-4">
            <div className="bg-white rounded-lg shadow-soft border border-dashboard-border overflow-hidden">
              <InteractiveAgent 
                sessionId={sessionId}
                onClearSession={handleClearSession}
              />
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}