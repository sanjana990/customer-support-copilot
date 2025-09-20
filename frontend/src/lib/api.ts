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
  }
};
