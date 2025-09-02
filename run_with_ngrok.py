from app.src import create_app
from pyngrok import ngrok
import sys

def start_ngrok():
    try:
        # Kill any existing ngrok processes first
        ngrok.kill()
        
        # Open a ngrok tunnel to the HTTP server
        public_url = ngrok.connect(5000).public_url
        print(f' * Running on {public_url}')
        print(f' * External URL accessible from anywhere: {public_url}')
        return public_url
    except Exception as e:
        print(f"Error starting ngrok: {str(e)}")
        sys.exit(1)

app = create_app()

if __name__ == '__main__':
    # Start ngrok
    start_ngrok()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000)
