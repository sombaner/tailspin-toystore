import { defineMiddleware } from "astro:middleware";

// Get server URL from environment variable with fallback for local development
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

/**
 * Generate a unique correlation ID for request tracking
 */
function generateCorrelationId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Log structured message in JSON format per Constitution Principle V
 */
function logStructured(
  level: 'INFO' | 'WARN' | 'ERROR', 
  message: string, 
  correlationId: string,
  extraFields: Record<string, any> = {}
): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    correlation_id: correlationId,
    service: 'tailspin-toystore-middleware',
    environment: process.env.NODE_ENV || 'development',
    ...extraFields
  };
  
  console.log(JSON.stringify(logEntry));
}

// Middleware to handle API requests
export const onRequest = defineMiddleware(async (context, next) => {
  
  // Guard clause: if not an API request, pass through to regular Astro handling
  if (!context.request.url.includes('/api/')) {
    return await next();
  }
  
  const url = new URL(context.request.url);
  const apiPath = url.pathname + url.search;
  
  // Generate or extract correlation ID
  const correlationId = context.request.headers.get('X-Correlation-ID') || generateCorrelationId();
  const startTime = Date.now();
  
  // Log incoming request
  logStructured('INFO', `Forwarding API request: ${context.request.method} ${apiPath}`, correlationId, {
    method: context.request.method,
    path: apiPath,
    target_url: `${API_SERVER_URL}${apiPath}`
  });
  
  // Create a new request to the backend server with correlation ID
  const serverRequest = new Request(`${API_SERVER_URL}${apiPath}`, {
    method: context.request.method,
    headers: {
      ...Object.fromEntries(context.request.headers),
      'X-Correlation-ID': correlationId
    },
    body: context.request.method !== 'GET' && context.request.method !== 'HEAD' ? 
          await context.request.clone().arrayBuffer() : undefined,
  });
  
  try {
    // Forward the request to the API server
    const response = await fetch(serverRequest);
    const data = await response.arrayBuffer();
    const duration = Date.now() - startTime;
    
    // Log successful response
    logStructured('INFO', `API request completed: ${context.request.method} ${apiPath} - ${response.status}`, correlationId, {
      method: context.request.method,
      path: apiPath,
      status_code: response.status,
      duration_ms: duration
    });
    
    // Return the response from the API server with correlation ID
    return new Response(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers),
        'X-Correlation-ID': correlationId
      },
    });
  } catch (error) {
    const duration = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    // Log error
    logStructured('ERROR', `Failed to forward API request: ${errorMessage}`, correlationId, {
      method: context.request.method,
      path: apiPath,
      error_type: error instanceof Error ? error.constructor.name : 'Unknown',
      duration_ms: duration
    });
    
    return new Response(JSON.stringify({ 
      error: 'Failed to reach API server',
      correlation_id: correlationId 
    }), {
      status: 502,
      headers: { 
        'Content-Type': 'application/json',
        'X-Correlation-ID': correlationId
      }
    });
  }
});