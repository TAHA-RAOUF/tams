# TAMS Backend-Frontend Integration Guide

This guide provides step-by-step instructions for integrating the TAMS (Technical Asset Management System) backend with a frontend application.

## Overview of the Integration

The TAMS backend is a Flask-based RESTful API with the following features:
- JWT authentication
- User management
- Anomaly management with AI predictions
- Maintenance windows management
- Action plans and action items
- Dashboard and reporting endpoints
- Data import functionality

## Step 1: Setup CORS for Cross-Origin Requests

**Backend Configuration:**

Ensure CORS is properly configured in the backend to accept requests from your frontend domain:

```python
# In main.py, verify that CORS is set up correctly
from flask_cors import CORS

# Setup with specific allowed origins (more secure)
CORS(app, resources={r"/api/*": {"origins": "https://your-frontend-domain.com"}})

# Or for development, allow all origins (less secure)
# CORS(app)
```

## Step 2: Understanding Authentication Flow

The backend uses JWT (JSON Web Tokens) for authentication. Your frontend needs to:

1. Send login credentials to `/api/v1/auth/login`
2. Store the returned JWT token (access_token)
3. Include this token in the Authorization header for all protected requests:
   - Format: `Authorization: Bearer <token>`
4. Handle token expiration (implement refresh token functionality or redirect to login)

## Step 3: API Endpoints Reference

The backend provides these main endpoint groups:

1. **Authentication**
   - `POST /api/v1/auth/register` - Create a new user account
   - `POST /api/v1/auth/login` - Authenticate and get JWT token
   - `GET /api/v1/auth/profile` - Get user profile
   - `PUT /api/v1/auth/profile` - Update user profile

2. **Anomalies**
   - `GET /api/v1/anomalies` - List all anomalies (with pagination)
   - `POST /api/v1/anomalies` - Create a new anomaly
   - `GET /api/v1/anomalies/<id>` - Get a specific anomaly
   - `PUT /api/v1/anomalies/<id>` - Update an anomaly
   - `DELETE /api/v1/anomalies/<id>` - Delete an anomaly
   - `PUT /api/v1/anomalies/<id>/status` - Update anomaly status
   - `PUT /api/v1/anomalies/<id>/predictions` - Edit predictions
   - `POST /api/v1/anomalies/<id>/approve` - Approve predictions
   - `POST /api/v1/anomalies/batch` - Create multiple anomalies
   - `PUT /api/v1/anomalies/bulk/status` - Update status of multiple anomalies

3. **Maintenance Windows**
   - `GET /api/v1/maintenance-windows` - List maintenance windows
   - `POST /api/v1/maintenance-windows` - Create a maintenance window
   - `GET /api/v1/maintenance-windows/<id>` - Get a specific window
   - `PUT /api/v1/maintenance-windows/<id>` - Update a window
   - `DELETE /api/v1/maintenance-windows/<id>` - Delete a window
   - `POST /api/v1/maintenance-windows/<id>/schedule-anomaly` - Schedule an anomaly

4. **Action Plans**
   - `GET /api/v1/action-plans/<anomaly_id>` - Get action plan for anomaly
   - `POST /api/v1/action-plans/<anomaly_id>` - Create an action plan
   - `PUT /api/v1/action-plans/<anomaly_id>` - Update an action plan
   - `POST /api/v1/action-plans/<id>/items` - Add action item
   - `PUT /api/v1/action-plans/<plan_id>/items/<item_id>` - Update item
   - `DELETE /api/v1/action-plans/<plan_id>/items/<item_id>` - Delete item

5. **Dashboard**
   - `GET /api/v1/dashboard/metrics` - Get key metrics
   - `GET /api/v1/dashboard/charts/anomalies-by-month` - Monthly anomalies
   - `GET /api/v1/dashboard/charts/anomalies-by-service` - Service distribution
   - `GET /api/v1/dashboard/charts/anomalies-by-criticality` - Criticality distribution
   - `GET /api/v1/dashboard/charts/maintenance-windows` - Maintenance timeline

6. **Predictions**
   - `POST /api/v1/predict` - Get prediction for a single equipment
   - `POST /api/v1/predict-batch` - Batch predictions
   - `POST /api/v1/predict-file` - Upload file for predictions

7. **Data Import**
   - `POST /api/v1/import/anomalies` - Import anomalies from CSV/Excel

## Step 4: Frontend Implementation Steps

### 4.1 Authentication Service

Create an authentication service in your frontend framework:

```javascript
// Example using JavaScript fetch API
class AuthService {
  async login(username, password) {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!response.ok) throw new Error('Login failed');
    
    const data = await response.json();
    // Store token in localStorage or secure cookie
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  }
  
  getToken() {
    return localStorage.getItem('token');
  }
  
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
  
  isAuthenticated() {
    return !!this.getToken();
  }
}
```

### 4.2 API Service

Create a base API service to handle requests:

```javascript
// Example API service
class ApiService {
  constructor() {
    this.baseUrl = '/api/v1';
    this.authService = new AuthService();
  }
  
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (this.authService.isAuthenticated()) {
      headers['Authorization'] = `Bearer ${this.authService.getToken()}`;
    }
    
    return headers;
  }
  
  async get(endpoint, params = {}) {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders()
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        this.authService.logout();
        window.location.href = '/login';
        throw new Error('Session expired');
      }
      throw new Error('Request failed');
    }
    
    return response.json();
  }
  
  async post(endpoint, data) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        this.authService.logout();
        window.location.href = '/login';
        throw new Error('Session expired');
      }
      throw new Error('Request failed');
    }
    
    return response.json();
  }
  
  // Similar methods for put, delete, etc.
}
```

### 4.3 Specialized Services

Create services for each resource type:

```javascript
// Example Anomaly Service
class AnomalyService extends ApiService {
  async getAllAnomalies(page = 1, perPage = 20) {
    return this.get('/anomalies', { page, per_page: perPage });
  }
  
  async getAnomaly(id) {
    return this.get(`/anomalies/${id}`);
  }
  
  async createAnomaly(anomalyData) {
    return this.post('/anomalies', anomalyData);
  }
  
  // Other methods for update, delete, etc.
}

// Similar services for MaintenanceService, ActionPlanService, etc.
```

### 4.4 Component Integration

In your frontend components:

```javascript
// Example React component
import React, { useState, useEffect } from 'react';
import { AnomalyService } from './services';

const AnomaliesList = () => {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const anomalyService = new AnomalyService();
  
  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        const data = await anomalyService.getAllAnomalies();
        setAnomalies(data.items);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchAnomalies();
  }, []);
  
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  
  return (
    <div>
      <h2>Anomalies</h2>
      <ul>
        {anomalies.map(anomaly => (
          <li key={anomaly.id}>
            {anomaly.num_equipement} - {anomaly.description}
            <span className="status">{anomaly.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

## Step 5: Route Protection

Implement route guards to protect frontend routes:

```javascript
// Example React route protection with React Router
import { Navigate, Outlet } from 'react-router-dom';
import { AuthService } from './services';

const ProtectedRoute = () => {
  const authService = new AuthService();
  
  if (!authService.isAuthenticated()) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
};

// Then in your routes:
<Route element={<ProtectedRoute />}>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/anomalies" element={<AnomaliesList />} />
  {/* Other protected routes */}
</Route>
```

## Step 6: File Uploads

For file upload endpoints:

```javascript
async uploadAnomaliesFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${this.baseUrl}/import/anomalies`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${this.authService.getToken()}`
      // Note: Don't set Content-Type here, it's set automatically for FormData
    },
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Upload failed');
  }
  
  return response.json();
}
```

## Step 7: Error Handling

Implement consistent error handling:

```javascript
// Enhanced API service with error handling
async request(endpoint, options = {}) {
  try {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers
      }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      // Handle specific error codes
      if (response.status === 401) {
        this.authService.logout();
        window.location.href = '/login';
        throw new Error('Session expired');
      }
      
      // Handle validation errors
      if (response.status === 400 && data.errors) {
        throw new ValidationError(data.errors);
      }
      
      throw new Error(data.message || 'Request failed');
    }
    
    return data;
  } catch (error) {
    // Log error to monitoring service
    console.error('API request failed:', error);
    throw error;
  }
}
```

## Step 8: Real-time Updates (Optional)

For real-time updates, consider adding WebSocket support:

1. Add a WebSocket server to the backend (e.g., with Socket.IO)
2. Create a WebSocket service in the frontend:

```javascript
// WebSocket service example with Socket.IO client
class WebSocketService {
  constructor() {
    this.socket = null;
    this.authService = new AuthService();
  }
  
  connect() {
    this.socket = io('/api/v1/socket', {
      auth: {
        token: this.authService.getToken()
      }
    });
    
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });
    
    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
    });
    
    return this.socket;
  }
  
  subscribe(event, callback) {
    if (!this.socket) this.connect();
    this.socket.on(event, callback);
  }
  
  unsubscribe(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }
}
```

## Step 9: Testing the Integration

1. Set up a proxy in your frontend development server to forward API requests
2. Test authentication flow
3. Test CRUD operations on all resources
4. Test file uploads
5. Test error scenarios and error handling

### Frontend Development Server Proxy Example

For React (in `package.json`):
```json
{
  "proxy": "http://localhost:5000"
}
```

For Angular (in `proxy.conf.json`):
```json
{
  "/api": {
    "target": "http://localhost:5000",
    "secure": false
  }
}
```

For Vue.js (in `vue.config.js`):
```javascript
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
}
```

## Step 10: Deployment Considerations

1. **Backend and Frontend on Same Domain:**
   - Deploy both to the same domain to avoid CORS issues
   - Configure web server (Nginx, Apache) to serve frontend files and proxy API requests

2. **Backend and Frontend on Different Domains:**
   - Configure CORS on backend to allow requests from frontend domain
   - Set absolute API URL in frontend code
   - Consider using a CDN for frontend assets

3. **Environment Configuration:**
   - Use environment variables for API URLs and other configuration
   - Create different configurations for development, staging, and production

### Nginx Configuration Example:

```nginx
server {
  listen 80;
  server_name your-domain.com;

  # Serve frontend files
  location / {
    root /path/to/frontend/build;
    try_files $uri $uri/ /index.html;
  }

  # Proxy API requests
  location /api/ {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }
}
```

## Conclusion

This guide provides the foundation for integrating your TAMS backend with a frontend application. Customize the implementation based on your specific frontend framework (React, Vue.js, Angular, etc.) and project requirements. The key is to establish a consistent pattern for authentication, API requests, error handling, and state management.

Remember to follow security best practices, such as:

- Storing JWT tokens securely
- Validating all user inputs
- Implementing proper error handling
- Using HTTPS for all API requests
- Implementing proper logging and monitoring

For a complete implementation, refer to the API documentation provided in the browsable API interface at `/api-browser/`.
