# Technical Report: PokeVault API

**Student Name:** Yichen Huang  
**Student ID:** 201656189  
**Date:** 10/03/2026

---

##  Deliverables & Project Links
* **1. Code Repository (GitHub):** https://github.com/Er1cSHelby/COMP3011_Coursework1.git
* **2. API Documentation (PDF):** [./API_Documentation.pdf](https://github.com/Er1cSHelby/COMP3011_Coursework1/blob/main/API_Documentation.pdf)
* **3. Presentation Slides (OneDrive):** [Microsoft OneDrive](https://leeds365-my.sharepoint.com/:p:/r/personal/sc222yh_leeds_ac_uk/Documents/Coursework%20slide%201.pptx?d=w272923d2d7b943c8841440a6aa66131a&csf=1&web=1&e=TADR0J)

---
## 1. Introduction

This report presents the design and architectural decisions underpinning the PokeVault API — a RESTful Web API developed for managing a Pokémon Trading Card Game (TCG) collection. The application enables users to maintain a personalised card collection, retrieve up-to-date card data from external sources, and evaluate both the total collection value and overall profit performance.
Live URL: https://Er1CShelby.pythonanywhere.com/api/

---

## 2. Technology Stack Choices

### 2.1 Programming Language: Python

**Justification:**
Python was selected as the implementation language for PokeVault API, as Python's clean and readable syntax significantly reduces development overhead, while its extensive ecosystem of libraries provides robust support for web development and API construction. The language also benefits from a large, active community and comprehensive documentation, ensuring reliable reference material throughout the development process.

### 2.2 Framework: Django + Django REST Framework (DRF)

**Justification:**
Django was chosen for its secure MVT architecture and built-in tools — admin interface, ORM, and authentication — reducing boilerplate and keeping focus on application logic. Django REST Framework extended this foundation with out-of-the-box serialization, viewsets, pagination, and filtering, making it a natural fit for building PokeVault's RESTful endpoints.

### 2.3 Database: SQLite

**Justification:**
SQLite was chosen for its zero-configuration setup and native Django integration, eliminating extra driver installation. It handles the anticipated load of under 10,000 records without the overhead of a full database server, and its single-file architecture makes the database trivially portable and easy to back up.

---

## 3. Architecture Design

### 3.1 Project Structure

```
├── manage.py            # Django command-line utility
├── fetch_data.py        # Custom script for external TCGdex API data ingestion
├── requirements.txt     # Project dependencies
├── db.sqlite3           # Local SQLite database
├── pokevault/           # Project configuration directory
│   ├── settings.py      # Global configuration
│   ├── urls.py          # Master URL routing
│   └── wsgi.py          # WSGI entry point for deployment
└── api/                 # Main application directory
    ├── __init__.py      # Package initialization
    ├── admin.py         # Django admin interface configuration
    ├── apps.py          # Application configuration
    ├── models.py        # Database schema definitions
    ├── serializers.py   # Data transformation for API responses
    ├── urls.py          # Application-level API routing
    ├── views.py         # Business logic and endpoint handling
    └── migrations/      # Database schema version control
```

### 3.2 API Design Principles

- **RESTful Architecture**: The API adheres to REST conventions, employing appropriate HTTP methods — GET, POST, PUT, PATCH, and DELETE — to represent each type of operation performed on a given resource
- **Read-Only for Reference Data**: Cards and Sets are read-only to maintain data integrity
- **Full CRUD for Collection**: Users have full control over their personal collection
- **Pagination**: Implemented for all list endpoints to handle large datasets efficiently

### 3.3 Data Models

Three core models were designed:
1. **ExpansionSet**: Represents a Pokémon TCG expansion set, serving as the top-level grouping entity for individual cards
2. **Card**: Individual cards with pricing from external TCGdex API
3. **CollectionItem**: Represents a user's personal collection entry, capturing ownership details and enabling collection value and profit calculations

---

## 4. External API Integration

### 4.1 TCGdex API

The application integrates with [https://api.tcgdex.net](https://api.tcgdex.net) to fetch real-time data, including card names, images, rarity, market prices, and set information.

### 4.2 Data Ingestion

A standalone fetch_data.py script automatically fetches API data, creates ExpansionSet records, populates Card records with metadata, and includes a fallback dataset for offline scenarios.

---

## 5. Challenges and Solutions

### 5.1 Challenge: External API Reliability

**Problem 1:** Several popular Pokémon TCG APIs was discovered that many of these services enforce strict paywalls, premium subscription tiers, or severe rate limits.

**Solution:** To ensure sustainable data ingestion without financial constraints, alternative open data sources were systematically researched. Consequently, heavily restricted APIs were completely replaced by the TCGdex API. TCGdex provides the necessary endpoint structures and comprehensive data freely, which perfectly aligns with the project's academic scope and ensures reliable database initialization.

**Problem 2:** Integration with the TCGdex API introduced two significant technical obstacles: network timeouts and excessively large JSON payloads. Attempting to fetch the entire card database — encompassing thousands of records — caused severe performance bottlenecks and frequent timeout exceptions during the local database ingestion process.

**Solution:**  fetch_data.py uses a dual-layered approach: API responses are capped at 50 cards for efficient local development, and a try-except fallback injects predefined FALLBACK_DATA if the request fails or times out — keeping the application operational in offline or network-restricted environments.

### 5.2 Challenge: Precision Loss in Financial Calculations

**Problem:** During development of the custom /analytics/value/ endpoint, calculating the total collection value produced type mismatch errors and floating-point precision issues. The root cause was a conflict between the DecimalField objects returned by the Django ORM — specifically purchase_price and average_price — and Python's native int type used for the quantity field when performing aggregate arithmetic operations.

**Solution:** The backend calculation logic was refactored to explicitly cast Django Decimal objects to Python floats during iteration. Additionally, the round(value, 2) function was applied prior to serialization, ensuring that all financial figures in the JSON response are consistently formatted to exactly two decimal places. This approach eliminates the risk of runtime errors and standardises the output format across all analytics endpoints.

### 5.3 Challenge: Enforcing Strict API Contracts (Defensive Programming)

**Problem:** Initially, the `CollectionItem` database model included a `default=1` parameter for the `quantity` field. This introduced a risk of "silent data corruption"—if a client application sent a malformed POST request missing the quantity parameter, the API would accept it and default to 1, rather than rejecting the invalid payload.

**Solution:** I removed the default parameter at the database schema level. By enforcing this strict constraint, Django REST Framework's serializers now automatically intercept incomplete payloads. This "fail-fast" architectural decision ensures the API strictly returns a `400 Bad Request` validation error, forcing client applications to adhere exactly to the documented API contract.

### 5.4 Challenge: RESTful Error Status Code Ambiguity

**Problem:** There was an architectural ambiguity regarding how to handle invalid relational data—specifically, determining the correct HTTP status code when a user attempts to add a non-existent `card_id` to their collection via a POST request. 

**Solution:** Following a thorough review of RESTful design principles, the DRF serializers were configured to clearly distinguish between these two error categories. The API now returns 400 Bad Request when a foreign key constraint violation occurs within the request body — indicating a client-side validation error — while strictly reserving 404 Not Found for cases where the requested URI endpoint itself references a non-existent resource. This separation ensures that error responses carry meaningful, unambiguous semantics for consuming clients.

### 5.5 Challenge: Cloud Deployment & Production Resilience

**Problem:** Deploying to PythonAnywhere's free tier revealed two production-specific issues. First, the platform's outbound HTTP whitelist blocked the TCGdex API, causing fetch_data.py to fail with a 403 Proxy Error. Second, the Django REST Framework UI lost its styling due to unmapped static assets.

**Solution:** To resolve these, the defensive fallback in fetch_data.py caught the proxy exception gracefully rather than crashing. The pre-populated local db.sqlite3 was manually uploaded to bypass network restrictions, providing examiners with a realistic dataset. Static assets were resolved by configuring the WSGI entry point and running collectstatic to map STATIC_ROOT, restoring the UI and ensuring the API remained fully accessible in production.

---

## 6. Testing Approach

Testing included Manual Testing (via curl for all endpoints), Django Admin (for data verification), and a custom /api/health/ endpoint. Coverage verified all CRUD operations for collection items, filtering functions, collection value calculations, and robust error handling (400, 404 responses).

---

## 7. Limitations

### 7.1 Current Limitations

Current limitations include a lack of user authentication, reliance on a single SQLite database limiting concurrent access, external dependency on the TCGdex API, and limited filtering options (only name/rarity). Crucially, regarding the domain model, the CollectionItem lacks a condition field (e.g., Mint, Heavily Played). Real-world TCG pricing is highly dependent on card condition, making the current /analytics/value/ calculation a simplified estimate.

---

## 8. Generative AI Declaration

### 8.1 AI Tools Used

During the development of this project, three Generative AI tools were employed for distinct, clearly defined purposes: Google Gemini, the OpenCode AI Assistant, and Claude Code.

1. **Gemini**: 
- Foundational Architecture Setup: Gemini was used to assist in generating the initial structural boilerplate and directory scaffolding for the Django and Django REST Framework project, accelerating the initial setup phase.
- Gemini was consulted to research and identify freely available external APIs, which led to the discovery and subsequent selection of the TCGdex API as the primary data source for Pokémon card information.

2. **OpenCode **: 
- Code Review and Debugging: OpenCode served as an automated quality assurance tool, used to troubleshoot runtime bugs, identify syntax errors, and refine data validation logic — including, for example, the removal of the default value from the quantity field.
- Documentation Refinement: The assistant was employed to review the README and API documentation, ensuring formatting consistency and identifying discrepancies between the written documentation and the actual codebase, such as misaligned pagination defaults and filter parameter definitions.

3. **Claude Code**: 
- Academic Report Polishing: Claude Code was used to refine and elevate the written quality of this project report. This included restructuring fragmented bullet points into cohesive academic prose, standardising tone and register throughout, improving logical flow between sections, and ensuring consistency in technical terminology across the document.

### 8.2 Analysis of AI Usage

AI assistance was confined to four categories: project scaffolding, external API research, quality assurance, and academic writing refinement. All core application logic — including the custom database models, viewsets, serializers, and the fetch_data.py ingestion script — was independently developed and integrated to meet the coursework requirements.

The use of AI followed academic integrity principles:
- AI was utilised as an enabler for initial setup, debugging assistance, and writing refinement, and not as a substitute for understanding the underlying MVT architectural concepts.
- All AI-generated boilerplate code, structural suggestions, documentation refinements, and report edits were manually reviewed and verified prior to integration into the final submission.
- Full responsibility for the entirety of the submitted codebase and report is assumed, with complete comprehension retained over all architectural decisions and their corresponding implementations.

---

## 9. Conclusion

The PokeVault API successfully demonstrates a RESTful web service built with Django and Django REST Framework. It provides essential functionality for managing a Pokemon card collection while integrating with external APIs for real-time data. The project highlights understanding of MVT architecture, API design, data modeling, and documentation practices required for the COMP3011 module.


