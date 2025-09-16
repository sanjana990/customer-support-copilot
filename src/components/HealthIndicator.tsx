import { Circle, Loader2, AlertTriangle } from 'lucide-react';
import { useApiHealth } from '@/hooks/useApiHealth';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

export function HealthIndicator() {
  const { health, isHealthy, isChecking, error, checkHealth } = useApiHealth();

  const getStatusColor = () => {
    if (isChecking) return 'text-warning';
    if (error) return 'text-danger';
    if (isHealthy) return 'text-success';
    return 'text-muted-foreground';
  };

  const getStatusIcon = () => {
    if (isChecking) return <Loader2 className="w-4 h-4 animate-spin" />;
    if (error) return <AlertTriangle className="w-4 h-4" />;
    return <Circle className={`w-4 h-4 fill-current ${getStatusColor()}`} />;
  };

  const getStatusText = () => {
    if (isChecking) return 'Checking...';
    if (error) return 'Disconnected';
    if (isHealthy) return 'Connected';
    return 'Unknown';
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          onClick={checkHealth}
          className="flex items-center gap-2 hover:bg-muted/50"
        >
          {getStatusIcon()}
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            API {getStatusText()}
          </span>
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <div className="space-y-1">
          <p className="font-semibold">API Health Status</p>
          <p className="text-sm text-muted-foreground">
            {error ? error : health?.message || 'Click to check health'}
          </p>
        </div>
      </TooltipContent>
    </Tooltip>
  );
}