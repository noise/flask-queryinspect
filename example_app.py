import logging
from flask import Flask
from flask.ext.queryinspect import QueryInspect

logging.basicConfig(format='%(asctime)-15s %(levelname)s %(message)s')
logging.getLogger('flask_queryinspect').setLevel(logging.DEBUG)

app = Flask(__name__)
QueryInspect(app)


@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
