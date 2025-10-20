import { useState, useEffect, useRef } from 'react';
import { logger, LogEntry, LogLevel } from '../../utils/logger';
import { ChevronDown, ChevronUp, Trash2, Download, Filter, Search } from 'lucide-react';

interface ConsoleProps {
  isOpen: boolean;
  onToggle: () => void;
}

export function Console({ isOpen, onToggle }: ConsoleProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<LogLevel | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Update logs every second
    const interval = setInterval(() => {
      setLogs(logger.getLogs());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (autoScroll && consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const filteredLogs = logs.filter(log => {
    const matchesFilter = filter === 'all' || log.level === filter;
    const matchesSearch = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.context?.component?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  const clearLogs = () => {
    logger.clearLogs();
    setLogs([]);
  };

  const exportLogs = () => {
    const data = logger.exportLogs();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audiovisuals-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getLevelColor = (level: LogLevel): string => {
    switch (level) {
      case 'debug': return 'text-gray-500 bg-gray-100';
      case 'info': return 'text-blue-600 bg-blue-100';
      case 'warn': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLevelCount = (level: LogLevel): number => {
    return logs.filter(log => log.level === level).length;
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={onToggle}
          className="bg-slate-800 hover:bg-slate-700 text-white p-3 rounded-lg shadow-lg border border-slate-600 transition-colors"
        >
          <ChevronUp className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 max-h-96 bg-slate-900 border border-slate-700 rounded-lg shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-white">Debug Console</h3>
          <div className="flex gap-1 text-xs">
            <span className={`px-1.5 py-0.5 rounded ${getLevelColor('error')}`}>
              {getLevelCount('error')}
            </span>
            <span className={`px-1.5 py-0.5 rounded ${getLevelColor('warn')}`}>
              {getLevelCount('warn')}
            </span>
            <span className={`px-1.5 py-0.5 rounded ${getLevelColor('info')}`}>
              {getLevelCount('info')}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={exportLogs}
            className="p-1 text-slate-400 hover:text-white transition-colors"
            title="Export logs"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={clearLogs}
            className="p-1 text-slate-400 hover:text-red-400 transition-colors"
            title="Clear logs"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={onToggle}
            className="p-1 text-slate-400 hover:text-white transition-colors"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="p-2 border-b border-slate-700">
        <div className="flex gap-2 mb-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as LogLevel | 'all')}
            className="text-xs bg-slate-800 border border-slate-600 rounded px-2 py-1 text-white"
          >
            <option value="all">All Levels</option>
            <option value="error">Errors</option>
            <option value="warn">Warnings</option>
            <option value="info">Info</option>
            <option value="debug">Debug</option>
          </select>
          
          <div className="flex-1 relative">
            <Search className="absolute left-2 top-1.5 w-3 h-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full text-xs bg-slate-800 border border-slate-600 rounded px-6 py-1 text-white placeholder-slate-400"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1 text-xs text-slate-400">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded"
            />
            Auto-scroll
          </label>
          <span className="text-xs text-slate-500">
            {filteredLogs.length} of {logs.length} logs
          </span>
        </div>
      </div>

      {/* Logs */}
      <div
        ref={consoleRef}
        className="h-64 overflow-y-auto p-2 text-xs font-mono"
      >
        {filteredLogs.length === 0 ? (
          <div className="text-center text-slate-500 py-8">
            No logs to display
          </div>
        ) : (
          filteredLogs.map((log, index) => (
            <div key={index} className="mb-1 p-2 rounded bg-slate-800/50">
              <div className="flex items-start gap-2">
                <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${getLevelColor(log.level)}`}>
                  {log.level.toUpperCase()}
                </span>
                <span className="text-slate-400 text-xs">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                {log.context?.component && (
                  <span className="text-slate-500 text-xs">
                    [{log.context.component}]
                  </span>
                )}
              </div>
              <div className="mt-1 text-white text-xs break-words">
                {log.message}
              </div>
              {log.context?.metadata && (
                <details className="mt-1">
                  <summary className="text-slate-400 text-xs cursor-pointer hover:text-white">
                    Context
                  </summary>
                  <pre className="mt-1 text-xs text-slate-300 bg-slate-900 p-2 rounded overflow-x-auto">
                    {JSON.stringify(log.context.metadata, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
