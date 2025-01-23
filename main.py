from flask import *
from public import public
from admin import admin
from buyer import buyer
from seller import seller
  

app = Flask(__name__)

app.register_blueprint(public)
app.register_blueprint(admin)
app.register_blueprint(buyer)
app.register_blueprint(seller)

app.secret_key = "ajdjdffasfkj"

app.run(debug=True, port=5006)
