from tmtn import create_app
app = create_app()

if __name__ == '__main__':
    try:
        app.run( host='0.0.0.0', port=5353, debug=True)
    except Exception as e:
        print(f"Error running the app: {e}")
