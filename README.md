# Atlan Customer Support Copilot Dashboard

A modern, deploy-friendly React + Vite application that integrates with the Atlan Customer Support Copilot API. Features AI-powered query classification, interactive chat agent, and comprehensive analytics dashboard.

![Dashboard Preview](https://via.placeholder.com/800x400/6366f1/ffffff?text=Atlan+Customer+Support+Dashboard)

## 🚀 Features

### 📊 Bulk Ticket Classification Dashboard
- **Expandable Ticket Rows**: Click any ticket to reveal detailed analysis
- **Classification Reasons**: See AI reasoning behind topic, sentiment, and priority decisions
- **Citations & Sources**: View documentation links and references
- **Real-time Metrics**: Processing time, confidence scores, and cache status
- **Smart Filtering**: Filter by priority, sentiment, and topic categories

### 🤖 Interactive AI Agent
- **Real-time Chat**: Conversational interface with the AI support agent
- **Internal Analysis**: Toggle to view classification reasoning for each response
- **Session Continuity**: Maintains conversation context across interactions
- **Citation Display**: Embedded source links and documentation references
- **Response Analytics**: View confidence scores and processing metrics

### ⚙️ Session Management
- **Automatic Session Handling**: UUID-based session management with localStorage persistence
- **Conversation History**: Load and view previous conversations
- **Session Clearing**: Reset conversations and start fresh
- **Cross-tab Sync**: Sessions persist across browser tabs

### 🔄 API Health Monitoring  
- **Real-time Status**: Live API connection status indicator
- **Auto-retry**: Automatic health checks every 30 seconds
- **Error Handling**: Graceful degradation with user feedback
- **Connection Recovery**: Smart reconnection handling

## 🛠️ Technical Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite 
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React Query for API state
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **API Client**: Custom fetch-based service

## 📋 Prerequisites

Before running this application, ensure you have:

- **Node.js** (v18.0.0 or higher)
- **npm** (v8.0.0 or higher) 
- **Atlan Customer Support Copilot API** running on `http://localhost:8000`

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd atlan-support-dashboard
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   
   Create or update the `.env` file:
   ```bash
   # Backend API Configuration
   VITE_BACKEND_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:8080`

## 🚀 Available Scripts

### Development
```bash
npm run dev          # Start development server with hot reload
```

### Building
```bash
npm run build        # Build for production
npm run preview      # Preview production build locally
```

### Code Quality
```bash
npm run lint         # Run ESLint for code quality checks
npm run lint:fix     # Auto-fix ESLint issues where possible
npm run type-check   # Run TypeScript type checking
```

## 🌐 Environment Configuration

### Required Environment Variables

| Variable | Description | Default Value | Required |
|----------|-------------|---------------|----------|
| `VITE_BACKEND_URL` | Backend API base URL | `http://localhost:8000` | Yes |

### Development Environment
```bash
# .env.development
VITE_BACKEND_URL=http://localhost:8000
```

### Production Environment
```bash
# .env.production  
VITE_BACKEND_URL=https://your-api-domain.com
```

## 🏗️ Build & Deploy

### Production Build
```bash
# Build the application
npm run build

# The built files will be in the `dist` directory
# Deploy the contents of `dist` to your web server
```

### Deploy to Popular Platforms

#### Vercel
```bash
npm install -g vercel
vercel --prod
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

#### Traditional Web Server
Upload the contents of the `dist` folder to your web server's document root.

## 📡 API Integration

### Backend API Requirements

The application expects the Atlan Customer Support Copilot API to be running with the following endpoints:

- `POST /api/query` - Submit queries and get AI responses
- `POST /api/query/conversation` - Submit follow-up queries
- `GET /api/conversation/{session_id}` - Retrieve conversation history
- `DELETE /api/conversation/{session_id}` - Clear conversation
- `GET /health` - API health check

### API Configuration

The app reads the backend URL from the `VITE_BACKEND_URL` environment variable. Ensure your API is:

1. **Running** on the specified URL
2. **CORS-enabled** for your frontend domain
3. **Returning proper JSON responses** as documented in `API_DOCUMENTATION.md`

## 🎨 UI Components & Styling

### Design System

The application uses a comprehensive design system built with:

- **Color Palette**: Professional blue/purple gradient theme
- **Typography**: Clean, modern font stack with proper hierarchy  
- **Components**: shadcn/ui component library with custom variants
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Mobile-first design approach

### Custom Component Variants

The app includes enhanced component variants:

```tsx
// Button variants
<Button variant="hero">Hero CTA</Button>
<Button variant="dashboard">Dashboard Action</Button>

// Badge variants  
<Badge variant="priority-p0">Critical</Badge>
<Badge variant="sentiment-positive">Happy</Badge>
```

## 🔧 Configuration Options

### Customizing the Dashboard

#### Adding New Classification Types

Update `src/types/api.ts` to add new classification categories:

```typescript
export type TopicType = "API/SDK" | "How-to" | "Connector" | "SSO" | "Product" | "NewCategory";
```

#### Modifying Colors & Themes

Update the design system in `src/index.css` and `tailwind.config.ts`:

```css
:root {
  --brand-primary: 250 84% 54%;  /* Update primary color */
  --brand-secondary: 260 75% 65%; /* Update secondary color */
}
```

#### Health Check Interval

Modify the health check frequency in `src/hooks/useApiHealth.ts`:

```typescript
// Check every 30 seconds (default)
const interval = setInterval(checkHealth, 30000);

// Check every minute
const interval = setInterval(checkHealth, 60000);
```

## 📱 Browser Support

- **Chrome** 90+
- **Firefox** 88+  
- **Safari** 14+
- **Edge** 90+

## 🐛 Troubleshooting

### Common Issues

#### API Connection Failed
```
Error: Failed to fetch
```
**Solution**: Verify the backend API is running on the correct URL specified in `VITE_BACKEND_URL`.

#### CORS Errors
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:8080' has been blocked by CORS policy
```
**Solution**: Configure CORS headers on your backend API to allow requests from your frontend domain.

#### Build Errors
```
Module not found: Can't resolve '@/components/...'
```
**Solution**: Ensure TypeScript path mapping is configured correctly in `tsconfig.json` and `vite.config.ts`.

### Debug Mode

Enable debug mode by adding to your `.env`:
```bash
VITE_DEBUG=true
```

### Logs & Monitoring

The application includes comprehensive error handling and logging:

- API errors are displayed as user-friendly toast notifications
- Network requests are logged in the browser console (development mode)
- Session management events are tracked in localStorage

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the existing code style
4. **Run tests**: `npm run lint && npm run type-check`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or questions:

- 📧 **Email**: support@atlan.com
- 📖 **Documentation**: See `API_DOCUMENTATION.md`
- 🐛 **Issues**: Create an issue in this repository

## 🔗 Related Resources

- [API Documentation](./API_DOCUMENTATION.md) - Complete backend API reference
- [Atlan Documentation](https://docs.atlan.com) - Official Atlan docs
- [React Documentation](https://react.dev) - React framework docs
- [Vite Documentation](https://vitejs.dev) - Vite build tool docs
- [Tailwind CSS](https://tailwindcss.com) - Styling framework docs

---

**Built with ❤️ by the Atlan Team**