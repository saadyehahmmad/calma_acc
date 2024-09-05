from tmtn import create_app, socketio

if __name__ == '__main__':
    app = create_app()
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error running the app: {e}")
