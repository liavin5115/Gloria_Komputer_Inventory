from app.src import create_app

app = create_app()

if __name__ == "__main__":
    # Added threaded=True for better handling of multiple connections
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)