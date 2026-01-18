# auth_backend (Flask)

Flask REST API for registration/login and basic user profile management, using:
- Password hashing via `werkzeug.security`
- JWT authentication via `PyJWT`
- SQLite persistence via `SQLAlchemy`

## Running

The preview system runs this service on port **3001**. `run.py` defaults to port 3001.

## Environment variables

This service supports these environment variables (all optional):

- `PORT` (default: `3001`)
- `SECRET_KEY` (default: `dev-secret-change-me`)  
  Used to sign JWT tokens. Set a strong random value in production.
- `JWT_EXPIRY_MINUTES` (default: `60`)
- `DATABASE_URL` (default: `sqlite:///./users.db`)  
  Example: `sqlite:///./users.db`

## Endpoints

Base URL (local): `http://localhost:3001`

### `POST /register`
Create a new user.

Request JSON:
```json
{
  "email": "user@example.com",
  "password": "min-8-chars",
  "display_name": "Optional Name",
  "bio": "Optional bio"
}
```

Responses:
- `201` returns the created profile (no password)
- `409` if email already exists

### `POST /login`
Authenticate and obtain JWT.

Request JSON:
```json
{ "email": "user@example.com", "password": "min-8-chars" }
```

Response `200`:
```json
{
  "access_token": "<jwt>",
  "token_type": "Bearer",
  "expires_in_minutes": 60
}
```

### `POST /logout`
Stateless JWT logout (server no-op); client should delete token.

### `GET /profile` (protected)
Requires header: `Authorization: Bearer <token>`

### `PUT /profile` (protected)
Update profile fields.

Request JSON:
```json
{ "display_name": "New Name", "bio": "New bio" }
```

### `GET /protected` (protected)
Example protected route.

## API Docs

Swagger UI is served under:
- `/docs` (UI)
- `/docs/openapi.json` (spec)
