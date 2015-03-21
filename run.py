#!/usr/bin/python3
from school import app
from config import Config

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)