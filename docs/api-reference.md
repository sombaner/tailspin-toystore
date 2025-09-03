# Tailspin Toys API Reference

The Tailspin Toys backend provides a REST API for accessing game data. This document describes all available endpoints, request/response formats, and error handling.

## Base URL

- **Development**: `http://localhost:5100`
- **Production**: Configure via `API_SERVER_URL` environment variable

## Authentication

The API currently does not require authentication. All endpoints are publicly accessible.

## Content Type

All API endpoints return JSON data with `Content-Type: application/json`.

## Error Handling

The API uses standard HTTP status codes and returns error information in JSON format:

```json
{
  "error": "Error description"
}
```

## Endpoints

### Games

#### Get All Games

Retrieves a list of all available games with their complete information including publisher and category details.

**Endpoint:** `GET /api/games`

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Game Title",
    "description": "Game description text",
    "starRating": 4.5,
    "publisher": {
      "id": 1,
      "name": "Publisher Name"
    },
    "category": {
      "id": 1,
      "name": "Category Name"
    }
  }
]
```

**Example:**
```bash
curl http://localhost:5100/api/games
```

#### Get Game by ID

Retrieves detailed information about a specific game.

**Endpoint:** `GET /api/games/{id}`

**Parameters:**
- `id` (integer, path parameter): The unique identifier of the game

**Response:** `200 OK`

```json
{
  "id": 1,
  "title": "Game Title",
  "description": "Detailed game description",
  "starRating": 4.5,
  "publisher": {
    "id": 1,
    "name": "Publisher Name"
  },
  "category": {
    "id": 1,
    "name": "Category Name"
  }
}
```

**Error Responses:**

- `404 Not Found`: Game with specified ID does not exist
```json
{
  "error": "Game not found"
}
```

**Example:**
```bash
curl http://localhost:5100/api/games/1
```

## Data Models

### Game Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier for the game |
| `title` | string | Yes | Game title (2-100 characters) |
| `description` | string | Yes | Game description (minimum 10 characters) |
| `starRating` | number/null | No | Average rating (0.0-5.0) |
| `publisher` | object/null | No | Publisher information (see Publisher Object) |
| `category` | object/null | No | Category information (see Category Object) |

### Publisher Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier for the publisher |
| `name` | string | Yes | Publisher name |

### Category Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier for the category |
| `name` | string | Yes | Category name |

## Database Schema

The API is backed by a SQLite database with the following relationships:

- **Games** table: Contains game information
- **Publishers** table: Contains publisher information
- **Categories** table: Contains category information
- **Relationships**: Each game belongs to one publisher and one category

## Rate Limiting

Currently, no rate limiting is implemented. However, please be respectful of the API and avoid excessive requests.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all origins to support frontend applications.

## Development Notes

- The API server runs on port 5100 by default
- Debug endpoints are available when `ENABLE_DEBUG_ENDPOINTS=true` is set
- The server supports hot reload during development

## Testing

The API includes comprehensive test coverage:

```bash
# Run API tests
cd server
python -m pytest tests/

# Run integration tests  
cd tests/e2e
npm test
```

For more information about testing, see the [E2E Test Documentation](../tests/e2e/README.md).