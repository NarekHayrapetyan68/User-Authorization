from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


if __name__ == "__main__":
    app.run(debug=True)