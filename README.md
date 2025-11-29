# 🗳️ Polly - Survey Application

Modern survey management system similar to Microsoft Forms, built with FastAPI and Vue.js.

## 📋 Features

- Create and manage surveys
- Collect responses
- View statistics
- Health monitoring dashboard
- RESTful API with automatic documentation
- Modern, responsive UI

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Vue 3 + TypeScript + Vite
- **Deployment**: Docker + Docker Compose

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd polly
```

2. Build and run the entire stack:
```bash
docker-compose up --build
```

3. Access the application:
   - **Frontend**: http://localhost
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### Manual Setup

#### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python -m app.main
```

The backend will be available at http://localhost:8000

#### Frontend

1. Navigate to client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## 🐳 Docker

### Backend Docker Image

Build:
```bash
cd backend
docker build -t polly-backend .
```

Run:
```bash
docker run -p 8000:8000 polly-backend
```

### Frontend Docker Image

Build:
```bash
cd client
docker build -t polly-frontend .
```

Run:
```bash
docker run -p 80:80 polly-frontend
```

## 📚 API Documentation

Once the backend is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

The server will run with hot-reload enabled.

### Frontend Development

```bash
cd client
npm install
npm run dev
```

The development server will run with hot-reload enabled.

### Linting and Formatting

Frontend:
```bash
cd client
npm run lint
npm run format
```

## 📁 Project Structure

```
polly/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── database.py
│       ├── models/
│       ├── routers/
│       └── services/
├── client/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│       ├── App.vue
│       ├── main.ts
│       ├── assets/
│       └── components/
└── docker-compose.yml
```

## 🔧 Environment Variables

### Backend

- `PORT`: Server port (default: 8000)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)

### Frontend

Create `.env` file in `client/` directory:

```env
VITE_API_URL=http://localhost:8000
```

For production (Docker), use `.env.production`:

```env
VITE_API_URL=http://backend:8000
```

## 🧪 Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd client
npm run test
```

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
