from flask import Flask

from src.test import test_bp

app = Flask(__name__)
app.register_blueprint(test_bp)


@app.route("/")
def hello():
    return "Hello World"


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
