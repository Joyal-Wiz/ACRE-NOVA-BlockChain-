from flask import *
from database import *

admin = Blueprint('admin',__name__)

@admin.route('/admin_home')
def admin_home():
  return render_template('admin_home.html')

@admin.route('/view_buyer')
def view_buyer():
  qry = "SELECT * FROM buyer"
  buyers = select(qry) 
  return render_template("view_buyer.html", buyers=buyers)

@admin.route('/view_seller')
def view_seller():
  qry = "SELECT * FROM seller"
  sellers = select(qry) 
  return render_template("view_seller.html", sellers=sellers)

@admin.route('/view_complaints')
def view_complaints():
  qry = "SELECT * FROM complaint"
  complaints = select(qry)
  return render_template("view_complaints.html",complaints=complaints)

@admin.route('/reply_complaint',methods = ['get','post'])
def reply_complaint():

    id = request.args['id']
    if 'submit' in request.form:
      reply = request.form['reply_textarea']
      qry = "UPDATE COMPLAINT SET REPLY ='%s' where complaint_id = '%s'  " %(reply,id)
      update(qry)
      return "<script>alert('replied successfuly');window.location='/view_complaints'</script>"
    return render_template("admin_reply.html")