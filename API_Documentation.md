# PokeVault API Documentation

**Student Name:** Yichen Huang  
**Student ID:** 201656189  

---

## 1. Introduction

The PokeVault API is a RESTful Web API built with Django and Django REST Framework. It provides endpoints for managing a Pokémon Trading Card Game (TCG) collection, including viewing card data and tracking collection value.

**Base URL:** `http://127.0.0.1:8000/api/`

---

## 2. Authentication

Currently, the API employs a dual-access model:
* **Public Endpoints:** No authentication is required for local development and demonstration. Read/Write operations on the `/collection/` and public `/cards/` are openly accessible.
* **Admin Operations:** Modifying the global source database (Adding new Cards or Sets globally) is protected and requires **Django Session Authentication**. This is managed via the built-in Django Admin interface (`/admin/`), strictly restricted to superuser accounts.

---

## 3. Error Responses

### 3.1 HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource successfully created |
| 204 | No Content - Request succeeded, no content to return |
| 400 | Bad Request - Invalid request body or parameters |
| 404 | Not Found - Resource does not exist |
| 500 | Internal Server Error - Server error |

### 3.2 Error Response Format

**400 Bad Request (Validation Error):**
```json
{
    "field_name": ["Error message describing the issue"]
}
```

Examples:
```json
{
    "card": ["This field is required."]
}
```
```json
{
    "quantity": ["A valid integer is required."]
}
```
```json
{
    "quantity": ["Ensure this value is greater than or equal to 1."]
}
```

**400 Bad Request (Invalid Data):**
```json
{
    "quantity": ["-1 is not a valid value."]
}
```
```json
{
    "purchase_price": ["-10.00 is not a valid value."]
}
```

**404 Not Found:**
```json
{
    "detail": "Not found."
}
```

**400 Bad Request (Invalid Foreign Key):**
```json
{
    "card": ["Invalid pk \"999\" - object does not exist."]
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Internal server error."
}
```

---

## 4. Data Models

### 4.1 ExpansionSet

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Auto-generated | Unique identifier |
| `name` | String | Required, max 100 chars | Name of the expansion set |
| `release_date` | Date | Nullable | Release date of the set |
| `total_cards` | Integer | Default 0 | Total number of cards in the set |

### 4.2 Card

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Auto-generated | Unique identifier |
| `name` | String | Required, max 100 chars | Name of the card |
| `rarity` | String | Required, must be one of: Common, Uncommon, Rare, Rare Holocarbon, Rare Ultra, Rare Secret | Rarity level |
| `set` | ForeignKey | Required, references ExpansionSet | Related expansion set |
| `average_price` | Decimal | Read-only (synced from external TCGdex API), default 0 | Average market price |
| `image_url` | String | Nullable | URL to card image |

### 4.3 CollectionItem

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Auto-generated | Unique identifier |
| `card` | ForeignKey | Required, references Card | Card being collected |
| `quantity` | Integer | Required, minimum 1 | Number of copies owned |
| `purchase_price` | Decimal | Optional, minimum 0, default 0 | Price paid per card |
| `date_added` | DateTime | Auto-generated, read-only | Timestamp when added |

---
## 5. Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sets/` | List all expansion sets |
| GET | `/sets/{id}/` | Retrieve a single expansion set |
| GET | `/cards/` | List all cards (with optional filtering) |
| GET | `/cards/{id}/` | Retrieve a single card |
| GET | `/collection/` | List all collection items |
| POST | `/collection/` | Create a new collection item |
| GET | `/collection/{id}/` | Retrieve a single collection item |
| PUT | `/collection/{id}/` | Update a collection item (full) |
| PATCH | `/collection/{id}/` | Update a collection item (partial) |
| DELETE | `/collection/{id}/` | Delete a collection item |
| GET | `/analytics/value/` | Calculate total collection value and profit |
| GET | `/health/` | Health check endpoint |

---

## 6. Endpoints Detail

### 6.1 Health Check

#### GET `/health/`

Check if the API is running.

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/health/
```

**Example Response:**
```json
{
    "status": "healthy",
    "service": "PokeVault API"
}
```

---

### 6.2 Expansion Sets (Read-Only)

#### GET `/sets/`

Retrieve a list of all expansion sets.

**Query Parameters:** None

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/sets/
```

**Example Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Base Set",
            "release_date": "1999-01-09",
            "total_cards": 102
        },
        {
            "id": 2,
            "name": "Jungle",
            "release_date": "1999-06-16",
            "total_cards": 64
        }
    ]
}
```

---

#### GET `/sets/{id}/`

Retrieve a single expansion set by ID.

**Path Parameters:**
- `id` (integer): The ID of the expansion set

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/sets/1/
```

**Example Response:**
```json
{
    "id": 1,
    "name": "Base Set",
    "release_date": "1999-01-09",
    "total_cards": 102
}
```

---

### 6.3 Cards (Read-Only)

#### GET `/cards/`

Retrieve a list of all cards. Supports filtering by name and rarity.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Filter by card name (case-insensitive partial match) |
| `rarity` | string | Filter by rarity (exact match) |

**Example Request - Get all cards:**
```bash
curl -X GET http://127.0.0.1:8000/api/cards/
```

**Example Request - Filter by name:**
```bash
curl -X GET "http://127.0.0.1:8000/api/cards/?name=Charizard"
```

**Example Request - Filter by rarity:**
```bash
curl -X GET "http://127.0.0.1:8000/api/cards/?rarity=Rare"
```

**Example Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Charizard",
            "rarity": "Rare",
            "set": {
                "id": 1,
                "name": "Base Set",
                "release_date": "1999-01-09",
                "total_cards": 102
            },
            "average_price": "150.00",
            "image_url": "https://example.com/charizard.png"
        }
    ]
}
```

---

#### GET `/cards/{id}/`

Retrieve a single card by ID.

**Path Parameters:**
- `id` (integer): The ID of the card

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/cards/1/
```

**Example Response:**
```json
{
    "id": 1,
    "name": "Charizard",
    "rarity": "Rare",
    "set": {
        "id": 1,
        "name": "Base Set",
        "release_date": "1999-01-09",
        "total_cards": 102
    },
    "average_price": "150.00",
    "image_url": "https://example.com/charizard.png"
}
```

---

### 6.4 Collection 

#### GET `/collection/`

Retrieve all items in your personal collection. No filtering is currently supported.

**Query Parameters:** None

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/collection/
```

**Example Response:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "card": 1,
            "card_detail": {
                "id": 1,
                "name": "Charizard",
                "rarity": "Rare",
                "set": {
                    "id": 1,
                    "name": "Base Set",
                    "release_date": "1999-01-09",
                    "total_cards": 102
                },
                "average_price": "150.00",
                "image_url": "https://example.com/charizard.png"
            },
            "quantity": 2,
            "purchase_price": "120.00",
            "date_added": "2026-01-15T10:30:00Z"
        }
    ]
}
```

---

#### POST `/collection/`

Add a new item to your collection.

**Request Body:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `card` | integer | Yes | Must be a valid Card ID | ID of the card to add |
| `quantity` | integer | Yes | Minimum 1 | Number of copies |
| `purchase_price` | decimal | No | Minimum 0, default 0 | Price paid per card |

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/collection/ \
  -H "Content-Type: application/json" \
  -d '{
    "card": 1,
    "quantity": 2,
    "purchase_price": 120.00
  }'
```

**Example Response (201 Created):**
```json
{
    "id": 1,
    "card": 1,
    "card_detail": {
        "id": 1,
        "name": "Charizard",
        "rarity": "Rare",
        "set": {
            "id": 1,
            "name": "Base Set",
            "release_date": "1999-01-09",
            "total_cards": 102
        },
        "average_price": "150.00",
        "image_url": "https://example.com/charizard.png"
    },
    "quantity": 2,
    "purchase_price": "120.00",
    "date_added": "2026-01-15T10:30:00Z"
}
```

---

#### GET `/collection/{id}/`

Retrieve a single collection item by ID.

**Path Parameters:**
- `id` (integer): The ID of the collection item

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/collection/1/
```

**Example Response:**
```json
{
    "id": 1,
    "card": 1,
    "card_detail": {
        "id": 1,
        "name": "Charizard",
        "rarity": "Rare",
        "set": {...},
        "average_price": "150.00",
        "image_url": "https://example.com/charizard.png"
    },
    "quantity": 2,
    "purchase_price": "120.00",
    "date_added": "2026-01-15T10:30:00Z"
}
```

---

#### PUT `/collection/{id}/`

Fully update a collection item (replaces all fields).

**Path Parameters:**
- `id` (integer): The ID of the collection item

**Request Body:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `card` | integer | Yes | Must be a valid Card ID | ID of the card |
| `quantity` | integer | Yes | Minimum 1 | Number of copies |
| `purchase_price` | decimal | No | Minimum 0, default 0 | Price paid per card |

**Example Request:**
```bash
curl -X PUT http://127.0.0.1:8000/api/collection/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "card": 1,
    "quantity": 5,
    "purchase_price": 100.00
  }'
```

**Example Response:**
```json
{
    "id": 1,
    "card": 1,
    "card_detail": {...},
    "quantity": 5,
    "purchase_price": "100.00",
    "date_added": "2026-01-15T10:30:00Z"
}
```

---

#### PATCH `/collection/{id}/`

Partially update a collection item.

**Path Parameters:**
- `id` (integer): The ID of the collection item

**Request Body:** At least one field required.

**Example Request:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/collection/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

**Example Response:**
```json
{
    "id": 1,
    "card": 1,
    "card_detail": {...},
    "quantity": 3,
    "purchase_price": "120.00",
    "date_added": "2026-01-15T10:30:00Z"
}
```

---

#### DELETE `/collection/{id}/`

Delete a collection item.

**Path Parameters:**
- `id` (integer): The ID of the collection item

**Example Request:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/collection/1/
```

**Response:** 204 No Content

---

### 6.5 Analytics

#### GET `/analytics/value/`

Calculate the total value and profit of the collection.

**Calculation Logic:**
- `total_value`: Sum of (card's `average_price` × `quantity`) for all collection items
- `total_cost`: Sum of (`purchase_price` × `quantity`) for all collection items
  - If `purchase_price` is null or not provided, defaults to 0
- `profit`: `total_value` - `total_cost`

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/analytics/value/
```

**Example Response:**
```json
{
    "total_value": 750.00,
    "total_cost": 240.00,
    "profit": 510.00
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `total_value` | decimal | Total market value (sum of card average_price × quantity) |
| `total_cost` | decimal | Total purchase cost (sum of purchase_price × quantity, treats null as 0) |
| `profit` | decimal | Profit (total_value - total_cost) |

---

## 7. Pagination

List endpoints use pagination with the following response format:

```json
{
    "count": 100,
    "next": "http://127.0.0.1:8000/api/cards/?page=2",
    "previous": null,
    "results": [...]
}
```

**Default:** 20 items per page

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `page` | Page number (default: 1) |
| `page_size` | Number of items per page (default: 20) |

---

## 8. Example Use Cases

### 8.1 Adding a Card to Collection

1. First, find the card ID:
```bash
curl -X GET "http://127.0.0.1:8000/api/cards/?name=Charizard"
```

2. Add to collection:
```bash
curl -X POST http://127.0.0.1:8000/api/collection/ \
  -H "Content-Type: application/json" \
  -d '{"card": 1, "quantity": 1, "purchase_price": 150.00}'
```

3. Check collection value:
```bash
curl -X GET http://127.0.0.1:8000/api/analytics/value/
```

---

## 9. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-03 | Initial release - Basic API structure with Django REST Framework |
| 1.1.0 | 2026-03-05 | Added pagination with 50 items default, 100 maximum per page |
| 1.2.0 | 2026-03-07 | Added card filtering by name and rarity parameters |
| 1.3.0 | 2026-03-10 | Added collection analytics with value and profit calculation |
