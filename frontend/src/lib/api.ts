// Basic API service for the application
export const apiService = {
  // Add your API methods here
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    return response.json();
  },
  
  async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  // Health check endpoint
  async getHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      throw new Error(`Health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  // Submit query endpoint
  async submitQuery(data: any) {
    try {
      const response = await fetch(`${this.baseURL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      throw new Error(`Query submission failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  },

  // Get tickets endpoint
  async getTickets() {
    try {
      const response = await fetch(`${this.baseURL}/tickets`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      throw new Error(`Failed to fetch tickets: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
};
