# Python Project

## Overview
This project is a Python application that implements core functionality and includes unit tests to ensure reliability.

## Installation
To install the required dependencies, run the following command:

```
pip install -r requirements.txt
```

## Usage
To run the application, execute the following command:

```
python src/main.py
```

## Running Tests
To run the unit tests, use the following command:

```
python -m unittest discover -s tests
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## Railway Deployment & Persistent Storage

This project is compatible with [Railway](https://railway.app/) persistent volumes. When deployed on Railway:

- The application uses the `/data` directory for database storage, as recommended by Railway best practices.
- The database file path is set via the `DATABASE_URL` environment variable (default: `/data/inventory.db`).
- The `/data` directory is automatically created if it does not exist.
- No Docker `VOLUME` keyword or manual volume mounting is required.

**Database persistence is ensured across deploys and restarts.**

If running locally, you can override `DATABASE_URL` to use a different path.