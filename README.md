# Bookstore API

This is a Django REST framework (DRF) API for managing bookstores, books, authors, and storing information.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Python](https://www.python.org/) (3.6 or higher)
- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [PostgreSQL](https://www.postgresql.org/)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/bookstore-api.git

2. Navigate to the project directory:

    ```bash
   cd bookstore-api

3. Install dependencies:

    ```bash
   pip install -r requirements.txt

4. Provide .env file with your credentials.

5. Create and apply migrations:

    ```bash
   python manage.py makemigrations
    python manage.py migrate

5. Run the development server:

    ```bash
   python manage.py runserver

## Endpoints

### Ping

- GET `/ping`

### Authors

- **Add Author**
    - POST `/author`
    - Request Body:

      ```json
      {
          "name": "Author Name",
          "birth_date": "YYYY-MM-DD"
      }
      ```
    - Response: 201 Created

- **Get Author**
    - GET `/author/{key}`
    - Response:

      ```json
      {
          "key": 1,
          "name": "Author Name"
      }
      ```

### Books

- **Add Book**
    - POST `/book`
    - Request Body:

      ```json
      {
          "barcode": "12345",
          "title": "Book Title",
          "publish_year": 2022,
          "author": {"name": "Author Name", "birth_date": "YYYY-MM-DD"}
      }
      ```
    - Response: 201 Created

- **Get Book**
    - GET `/book/{key}`
    - Response:

      ```json
      {
          "key": 1,
          "barcode": "12345",
          "title": "Book Title",
          "publish_year": 2022,
          "author": {"name": "Author Name", "birth_date": "YYYY-MM-DD"},
          "quantity": 5
      }
      ```

- **Search by Barcode**
    - GET `/book?barcode=...`
    - Response:

      ```json
      {
          "found": 2,
          "items": [
              {
                  "key": 1,
                  "barcode": "12345",
                  "title": "Book Title",
                  "publish_year": 2022,
                  "author": {"name": "Author Name", "birth_date": "YYYY-MM-DD"},
                  "quantity": 5
              },
              {
                  "key": 2,
                  "barcode": "123456",
                  "title": "Another Book",
                  "publish_year": 2021,
                  "author": {"name": "Author Name", "birth_date": "YYYY-MM-DD"},
                  "quantity": 3
              }
          ]
      }
      ```

### Storing

- **Add Leftover**
    - POST `/leftover/add`
    - Request Body:

      ```json
      {
          "barcode": "12345",
          "quantity": 3
      }
      ```
    - Response: 201 Created

- **Remove Leftover**
    - POST `/leftover/remove`
    - Request Body:

      ```json
      {
          "barcode": "12345",
          "quantity": 2
      }
      ```
    - Response: 201 Created

- **Bulk Leftovers from File**
    - POST `/leftovers/bulk`
    - Upload an Excel or TXT file with barcode and quantity information.

### History

- **Get Storing History**
    - GET `/history?start={YYYY-MM-DD}&end={YYYY-MM-DD}&book={key}`
    - Query parameters are optional.
    - Response:

      ```json
      [
          {
              "book": {"key": 1, "title": "Book Title", "barcode": "12345"},
              "start_balance": 5,
              "end_balance": 3,
              "history": [
                  {"date": "2022-01-15", "quantity": 2},
                  {"date": "2022-01-16", "quantity": 5},
                  {"date": "2022-01-18", "quantity": -4}
              ]
          }
      ]
      ```