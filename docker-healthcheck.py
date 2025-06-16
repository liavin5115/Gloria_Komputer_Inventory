import http.client
import sys
import os

def check_health():
    try:
        conn = http.client.HTTPConnection('localhost:5000', timeout=2)
        conn.request('GET', '/')
        response = conn.getresponse()
        
        if response.status == 200:
            return True
        else:
            print(f"Health check failed with status: {response.status}")
            return False
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    sys.exit(0 if check_health() else 1)
