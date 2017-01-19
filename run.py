from app import app

app.config.from_json('../config.json')

if __name__ == '__main__':
    app.run()
