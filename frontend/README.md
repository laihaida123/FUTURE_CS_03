# Secure File Portal - Vue Frontend

This is the Vue.js frontend for the Secure File Portal application. It communicates with the Flask backend via RESTful APIs.

## Project Setup

### Prerequisites
- Node.js (version 14 or higher)
- npm or yarn

### Install Dependencies

```bash
npm install
```

### Compiles and hot-reloads for development

```bash
npm run serve
```

### Compiles and minifies for production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html           # Main HTML template
├── src/
│   ├── assets/              # Static assets
│   ├── components/          # Reusable Vue components
│   ├── views/               # Page-level components
│   ├── router/              # Vue Router configuration
│   ├── App.vue              # Root Vue component
│   └── main.js              # Entry point
├── package.json             # Project dependencies and scripts
└── vue.config.js            # Vue CLI configuration
```

## Development Workflow

1. Make sure the Flask backend is running on `http://localhost:5000`
2. Run `npm run serve` to start the development server
3. Access the application at `http://localhost:8080`

## API Integration

The frontend communicates with the backend via the `/api` endpoints:

- `POST /api/login` - User authentication
- `GET /api/files` - List available files
- `POST /api/upload` - Upload and encrypt a file
- `GET /api/download/<filename>` - Download and decrypt a file

The development server is configured with a proxy to forward API requests to the Flask backend.

## Authentication

The application uses JWT (JSON Web Tokens) for authentication:

1. On login, the backend returns a JWT token
2. The frontend stores the token in localStorage
3. For authenticated requests, the token is sent in the Authorization header
4. On logout, the token is removed from localStorage

## Building for Production

To build the application for production:

```bash
npm run build
```

The built files will be in the `dist/` directory, which can be served by any static file server.