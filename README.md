
# Books Review Project with Ollama Integration

Welcome to the Books Review Project! This project enables users to manage books and their reviews by utilizing the integration of Ollama and Tesseract, allowing for the processing of scanned PDFs and images to enhance functionality. Below, you will find detailed installation instructions, project setup, and usage guidelines.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Tesseract Installation](#tesseract-installation)
5. [Database Configuration](#database-configuration)
6. [Security Configuration](#security-configuration)
7. [Database Migration](#database-migration)
8. [Running the Project](#running-the-project)
9. [Testing](#testing)
10. [Usage](#usage)
11. [License](#license)

## Project Overview

The Books Review Project is designed to provide a platform for users to:

- **Add, retrieve, update, and delete books.**
- **Write and manage reviews for each book.**
- **Generate book summaries and recommendations using the Ollama integration.**

## Requirements

Before you begin, ensure you have the following software installed:

- **Docker**
- **Python 3.11 or later**
- **pip** for managing Python packages
- **Alembic** for database migrations
- **Tesseract OCR** for optical character recognition

## Installation

Follow these steps to set up the Ollama integration and project dependencies:

### 1. Install Ollama Without a GPU

Run the following command to start the Ollama service using Docker:

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 2. Run the Ollama Model

Execute the following command to run the Llama3 model:

```bash
docker exec -it ollama ollama run llama3
```

### 3. Set Up the Python Environment

Create a virtual environment for the project:

```bash
python -m venv .venv
```

Activate the virtual environment:

- On **Windows**:

  ```bash
  .venv\Scripts\activate
  ```
- On **macOS/Linux**:

  ```bash
  source .venv/bin/activate
  ```

### 4. Install Project Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Tesseract Installation

To install Tesseract OCR, follow these instructions based on your operating system:

### Windows

1. Download the Tesseract installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer and follow the setup instructions.
3. Add Tesseract to your system PATH:

   - Search for "Environment Variables" in the Windows search bar.
   - Click on "Environment Variables".
   - In the "System variables" section, find the `Path` variable and click "Edit".
   - Add the path to the Tesseract installation (e.g., `C:\Program Files\Tesseract-OCR`).
4. Verify the installation by running the following command in Command Prompt:

   ```bash
   tesseract --version
   ```
5. 

## Database Configuration

Ensure you have the following database configuration in your environment:

```plaintext
db_host=db.postgres.database.azure.com
db_port=5432
db_name=jktech
db_pwd=arxt%40123
db_usr=postgres
MIGRATION_DATABASE_URL=postgresql+psycopg2://postgres:arxt%%40123@db.postgres.database.azure.com:5432/jktech
```

## Security Configuration

Configure your application with the following settings:

```plaintext
secret_key="your_secret_key"
refresh_secret_key="your_refresh_secret_key"
algorithm="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1800
CHARACTER_LIMIT=4000  # This is an example limit; adjust based on your model’s capabilities
model='llama3.1'
```

## Database Migration

To handle database migrations using Alembic, you can use the following commands:

1. **Create Initial Migration**:

   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```
2. **Add Migration for Book Model**:

   ```bash
   alembic revision --autogenerate -m "add book"
   ```
3. **Apply Migrations**:

   ```bash
   alembic upgrade head
   ```

## Running the Project

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

You can now access the application at:

- [http://127.0.0.1:8000](http://127.0.0.1:8000) - Main application
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) - Swagger documentation

## Testing

To run the tests for the project, use the following command:

```bash
pytest test/test_suite.py --run test
```

This will execute the test suite and display the results in your terminal.

## Usage

Once the application is running, you can perform the following actions:

- **Manage Books**: Add new books, view existing books, update details, and delete books.
- **Write Reviews**: For each book, users can submit reviews and manage them accordingly.
- **Ollama Integration**: Utilize the Ollama API to generate summaries and recommendations based on user input.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

Feel free to adjust any details further as necessary!
