from app.src import create_app

app = create_app()

# Only include the following for local development, not for Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)