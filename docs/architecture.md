# Architecture

```text
Static landing page
       |
       v
FastAPI routes ---- Pydantic validation
       |
       +---- SQLAlchemy ---- SQLite (default) / PostgreSQL
       |
       +---- ML inference ---- saved Scikit-learn Pipeline
       |
       +---- Memory notes ---- relational storage
```

## Boundaries
- `src/data`: synthetic dataset creation
- `src/features`: canonical model feature definitions
- `src/training`: preprocessing, training, candidate comparison, serialization
- `src/inference`: loading the persisted pipeline and prediction
- `backend/api`: HTTP contract and status codes
- `backend/services.py`: application logic
- `backend/models.py`: relational persistence schema

The landing page is static HTML/CSS and is served by FastAPI. It is not a React application.
