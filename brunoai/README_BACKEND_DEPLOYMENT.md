# Bruno AI Backend Deployment Guide

This document provides instructions for deploying the Bruno AI backend application locally using Docker Compose. Ensure that Docker and Docker Compose are installed on your machine before proceeding.

## Prerequisites

- Docker: Make sure Docker is installed and running on your system.
- Docker Compose: Ensure the Docker Compose command-line tool is installed.
- Environment Variables: Create a `.env` file in the project root directory and set up environment variables using the `.env.example` as a reference.

## Local Deployment Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/bruno-ai-backend.git
   cd bruno-ai-backend
   ```

2. **Copy environment configuration**

   ```bash
   cp .env.example .env
   # Customize your environment variables in the `.env` file
   ```

3. **Build and start the services**

   ```bash
   docker-compose up --build
   ```

   This command will build images and start the containers for PostgreSQL, Redis, and the backend API service.

4. **Access the API**

   - The API server will be accessible at `http://localhost:3000`.
   - Health check endpoint is available at `http://localhost:3000/health`.

5. **Database Initialization**

   The database schema will be initialized automatically using the script located in `backend/database/init/001_init.sql`.

6. **Stopping and removing containers**

   To stop and remove the running containers without removing the data, use:

   ```bash
   docker-compose down
   ```

## Notes

- **Development Mode**: When working in development mode, consider mounting the source code directory to the container for live code changes.

  ```yaml
  # Example of mounting the host code directory (Add to docker-compose.yml)
  volumes:
    - ./backend:/app
  ```

- **Docker Commands**: Familiarize yourself with basic Docker commands to help manage containers effectively.

- **Customization**: Modify configurations in `docker-compose.yml`, `nginx.conf`, and the `.env` file according to your deployment needs.

For more detailed configuration and customization, refer to individual service Dockerfile and configuration settings.

Enjoy deploying Bruno AI locally! 😊

