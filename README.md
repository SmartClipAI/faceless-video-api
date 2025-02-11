# Faceless API

A FastAPI-based service for image and audio generation.

## Features

- Image processing and generation
- Audio generation
- Token authentication
- RESTful API endpoints

## Requirements

- Python 3.8+
- PostgreSQL database

## Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/faceless-api.git
cd faceless-api
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Environment Configuration

Copy the environment template and configure the variables:
```bash
cp .env.example .env
```

Required environment variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

## Database Setup

1. Ensure PostgreSQL is running
2. Create database
```bash
createdb faceless_db  # Using PostgreSQL CLI
```

3. Initialize database tables
```bash
python -m app.scripts.run_init_db
```

## Running the Service

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

After starting the service, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

For detailed API documentation, see [docs/api.md](docs/api.md)

## Project Structure

```
faceless-api/
├── app/
│   ├── core/          # Core configurations
│   ├── schemas/       # Pydantic models
│   ├── services/      # Business logic
│   ├── scripts/       # Utility scripts
│   └── main.py        # Application entry point
├── docs/              # Documentation
├── requirements.txt   # Project dependencies
└── README.md
```

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

## Support

For issues and questions, please create a GitHub Issue.