import { invoke } from '@tauri-apps/api/core';
import { attachConsole } from '@tauri-apps/plugin-log';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogContext {
  component?: string;
  action?: string;
  userId?: string;
  sessionId?: string;
  metadata?: Record<string, any>;
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: LogContext;
}

class Logger {
  private sessionId: string;
  private isEnabled: boolean = true;
  private logBuffer: LogEntry[] = [];
  private maxBufferSize: number = 1000;
  private originalConsole: Partial<Console> | null = null;
  private pluginConsoleAttached = false;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.originalConsole = { ...console };
    this.attachPluginConsole();
    this.setupConsoleLogging();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async attachPluginConsole(): Promise<void> {
    try {
      await attachConsole();
      this.pluginConsoleAttached = true;
    } catch (error) {
      this.originalConsole?.warn?.call(
        console,
        'Failed to attach plugin console stream:',
        error,
      );
    }
  }

  private setupConsoleLogging(): void {
    if (!this.originalConsole) {
      this.originalConsole = { ...console };
    }

    console.log = (...args) => {
      this.log('info', args.join(' '), { component: 'console' });
      const original = this.originalConsole?.log;
      original?.apply(console, args as unknown as any[]);
    };

    console.warn = (...args) => {
      this.log('warn', args.join(' '), { component: 'console' });
      const original = this.originalConsole?.warn;
      original?.apply(console, args as unknown as any[]);
    };

    console.error = (...args) => {
      this.log('error', args.join(' '), { component: 'console' });
      const original = this.originalConsole?.error;
      original?.apply(console, args as unknown as any[]);
    };

    console.debug = (...args) => {
      this.log('debug', args.join(' '), { component: 'console' });
      const original = this.originalConsole?.debug;
      original?.apply(console, args as unknown as any[]);
    };
  }

  private async sendToBackend(entry: LogEntry): Promise<void> {
    try {
      await invoke('log_message', {
        level: entry.level,
        message: entry.message,
        context: entry.context ? JSON.stringify(entry.context) : null,
      });
    } catch (error) {
      // Fallback to console if backend logging fails
      this.originalConsole?.error?.call(console, 'Failed to send log to backend:', error);
    }
  }

  private addToBuffer(entry: LogEntry): void {
    this.logBuffer.push(entry);
    
    // Maintain buffer size
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize);
    }
  }

  async log(level: LogLevel, message: string, context?: LogContext): Promise<void> {
    if (!this.isEnabled) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: {
        ...context,
        sessionId: this.sessionId,
      },
    };

    // Add to buffer
    this.addToBuffer(entry);

    // Send to backend
    await this.sendToBackend(entry);

    // Log to browser console with styling
    this.logToConsole(entry);
  }

  private logToConsole(entry: LogEntry): void {
    const styles = {
      debug: 'color: #6B7280; background: #F3F4F6; padding: 2px 4px; border-radius: 3px;',
      info: 'color: #3B82F6; background: #DBEAFE; padding: 2px 4px; border-radius: 3px;',
      warn: 'color: #F59E0B; background: #FEF3C7; padding: 2px 4px; border-radius: 3px;',
      error: 'color: #EF4444; background: #FEE2E2; padding: 2px 4px; border-radius: 3px;',
    };

    const prefix = `%c[${entry.level.toUpperCase()}]`;
    const timestamp = new Date(entry.timestamp).toLocaleTimeString();
    const contextStr = entry.context ? ` | ${JSON.stringify(entry.context)}` : '';
    
    this.originalConsole?.log?.call(
      console,
      `${prefix} ${timestamp}${contextStr} ${entry.message}`,
      styles[entry.level],
    );
  }

  // Convenience methods
  debug(message: string, context?: LogContext): Promise<void> {
    return this.log('debug', message, context);
  }

  info(message: string, context?: LogContext): Promise<void> {
    return this.log('info', message, context);
  }

  warn(message: string, context?: LogContext): Promise<void> {
    return this.log('warn', message, context);
  }

  error(message: string, context?: LogContext): Promise<void> {
    return this.log('error', message, context);
  }

  // Performance logging
  async time(label: string): Promise<void> {
    await this.log('debug', `Timer started: ${label}`, { action: 'timer_start' });
  }

  async timeEnd(label: string): Promise<void> {
    await this.log('debug', `Timer ended: ${label}`, { action: 'timer_end' });
  }

  // API call logging
  async apiCall(method: string, url: string, status?: number, duration?: number): Promise<void> {
    await this.log('info', `API ${method} ${url}`, {
      action: 'api_call',
      metadata: { method, url, status, duration },
    });
  }

  // User action logging
  async userAction(action: string, component?: string, metadata?: Record<string, any>): Promise<void> {
    await this.log('info', `User action: ${action}`, {
      action,
      component,
      metadata,
    });
  }

  // Error logging with stack trace
  async logError(error: Error, context?: LogContext): Promise<void> {
    await this.log('error', error.message, {
      ...context,
      metadata: {
        ...context?.metadata,
        stack: error.stack,
        name: error.name,
      },
    });
  }

  // Get logs for debugging
  getLogs(): LogEntry[] {
    return [...this.logBuffer];
  }

  // Clear logs
  clearLogs(): void {
    this.logBuffer = [];
  }

  // Enable/disable logging
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  // Get session ID
  getSessionId(): string {
    return this.sessionId;
  }

  // Export logs as JSON
  exportLogs(): string {
    return JSON.stringify(this.logBuffer, null, 2);
  }
}

// Create singleton instance
export const logger = new Logger();

// Export convenience functions
export const log = {
  debug: (message: string, context?: LogContext) => logger.debug(message, context),
  info: (message: string, context?: LogContext) => logger.info(message, context),
  warn: (message: string, context?: LogContext) => logger.warn(message, context),
  error: (message: string, context?: LogContext) => logger.error(message, context),
  time: (label: string) => logger.time(label),
  timeEnd: (label: string) => logger.timeEnd(label),
  apiCall: (method: string, url: string, status?: number, duration?: number) => 
    logger.apiCall(method, url, status, duration),
  userAction: (action: string, component?: string, metadata?: Record<string, any>) => 
    logger.userAction(action, component, metadata),
  logError: (error: Error, context?: LogContext) => logger.logError(error, context),
};

export default logger;
