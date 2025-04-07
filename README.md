# Health Stats Data Processor

A Python-based microservice for processing and analyzing health statistics data.

## Features

- Process health records from various file formats (CSV, Excel)
- Extract and standardize health parameters
- Calculate trends and detect anomalies
- Generate health scores
- Provide reference ranges for common health parameters
- RESTful API with FastAPI
- MongoDB integration for data storage
- JWT-based authentication

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_NAME=health_stats
SECRET_KEY=your-secret-key-here
```

4. Run the application:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /api/health-records/upload`: Upload and process health records
- `GET /api/health-records/records`: Get user's health records
- `GET /api/analysis/trends/{parameter}`: Get trends for a specific parameter
- `GET /api/analysis/anomalies`: Detect anomalies in health parameters
- `GET /api/analysis/health-score`: Get overall health score
- `GET /api/analysis/reference-ranges`: Get reference ranges for parameters

## Testing

Run tests using pytest:
```bash
pytest
```

## Project Structure

```
data-processor/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   ├── models/
│   │   └── health_record.py
│   ├── routers/
│   │   ├── health_records.py
│   │   └── analysis.py
│   └── services/
│       ├── data_processor.py
│       └── analysis.py
├── tests/
│   └── test_data_processor.py
├── config/
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the ISC License.
