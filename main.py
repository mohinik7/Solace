from website import create_app
import signal
import sys

app = create_app()

def signal_handler(sig, frame):
    print('\nShutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    print("Initializing Chatbot.........")
    app.run(debug=True, use_reloader=True)
 