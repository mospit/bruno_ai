# Bruno AI Quick-Start Guide for Testers

## Prerequisites

Before testing Bruno AI, ensure the following prerequisites are met:

- **Flutter SDK**: Version 3.19.0 or later.
- **Dart SDK**: Version 3.3.0 or later.
- **Node.js**: Version 18.0.0 or later (for backend API).
- **Docker**: Install and ensure Docker Desktop is running.
- **Git**: Install Git for version control.

## Environment Variables

Create a `.env` file in the project root and define the following environment variables:

```
# API Configuration
API_PORT=3000
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000,https://bruno-ai.app

# Database Configuration
POSTGRES_PASSWORD=bruno_secure_pass_2024

# Redis Configuration
REDIS_PASSWORD=redis_secure_pass_2024

# JWT Secret
JWT_SECRET=bruno_jwt_secret_key_2024_change_this_in_production

# External API Keys
INSTACART_API_KEY=your_instacart_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Refer to `.env.example` for complete configuration options.

## Known Limitations

- **Real-time Features**: No real-time data sync implemented yet.
- **Scalability**: Application is in MVP stage; performance optimizations are ongoing.
- **API Endpoints**: Some API endpoints are placeholders and need final implementation.
- **Mobile Features**: iOS build support is limited; full TestFlight integration is pending.

## Testing Procedures

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/bruno-ai.git
   cd bruno-ai
   ```

2. **Install Dependencies**
   ```bash
   flutter pub get
   npm install --prefix ./backend
   ```

3. **Run Backend Services**
   Utilize Docker to start backend services:
   ```bash
   docker-compose up --build
   ```

4. **Run the Flutter Application**
   Start the Flutter app for development:
   ```bash
   flutter run
   ```

## Feedback and Issues

Report any bugs or issues to the project's GitHub repository by creating an issue.
For assistance, contact the support team via support@bruno-ai.com.

Enjoy testing Bruno AI! 🐻
