from flask import Flask

app = Flask(__name__)
import routes.square
import routes.klotski
import routes.digitalcolony

