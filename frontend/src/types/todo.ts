/**
 * Todo item interface representing the data model from the API
 */
export interface Todo {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Data structure for creating a new todo (without server-generated fields)
 */
export interface NewTodo {
  title: string;
  description: string;
  completed?: boolean;
}

/**
 * Data structure for updating an existing todo
 * All fields are optional as partial updates are supported
 */
export interface UpdateTodo {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * API error response structure
 */
export interface ApiError {
  error: string;
}

/**
 * API success message response
 */
export interface ApiSuccessMessage {
  message: string;
}

/**
 * Health check response from the API
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  database?: string;
  error?: string;
}
