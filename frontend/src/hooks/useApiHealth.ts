import { useState, useEffect } from 'react';
import { apiService } from '@/lib/api';
import { HealthResponse } from '@/types/api';

export function useApiHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setIsChecking(true);
    setError(null);
    
    try {
      const response = await apiService.getHealth();
      setHealth(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Health check failed');
      setHealth(null);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkHealth();
    
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return {
    health,
    isHealthy: health?.status === 'healthy',
    isChecking,
    error,
    checkHealth,
  };
}