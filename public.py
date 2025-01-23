from flask import *
from database import *

public = Blueprint('public',__name__)

@public.route('/')
def home():
  return render_template('index.html')


@public.route('/login',methods=['get','post'])
def login():
  if 'log' in request.form:
    username = request.form['username']
    password = request.form['password']
    
    qry="select * from login where username='%s' and password='%s'"%(username,password)
    res=select(qry)
    
    # print(res)
    session['log']=res[0]['login_id']

    if res[0]['usertype']=='buyer':
      qry1="select * from buyer where login_id='%s'"%(session['log'])
      res1=select(qry1)
      if res1:
        session['buyer']=res1[0]['buyer_id']
        return redirect(url_for('buyer.buyer_home'))
    elif res[0]['usertype']=='seller':
      qry1="select * from seller where login_id='%s'"%(session['log'])
      res1=select(qry1)
      if res1:
        session['seller']=res1[0]['seller_id']
        return redirect(url_for('seller.seller_home'))
    elif res[0]['usertype']=='admin':
      return redirect(url_for('admin.admin_home'))
      


  return render_template('login.html')

@public.route('/buyer',methods=['get','post'])
def buyer():
  if 'submit' in request.form:
    firstname=request.form['firstname']
    lastname=request.form['lastname']
    housename=request.form['housename']
    email=request.form['email']
    phone=request.form['phone']
    place=request.form['place']
    pincode=request.form['pincode']
    username=request.form['username']
    password=request.form['password']

    qry="insert into login values(null,'%s','%s','buyer')"%(username,password)
    res=insert(qry)

    qry1="insert into buyer values(null,'%s','%s','%s','%s','%s','%s','%s','%s')"%(firstname,lastname,housename,email,phone,res,place,pincode)
    insert(qry1)



  return render_template('buyer.html')

@public.route('/seller',methods=['get','post'])
def seller():
  if 'submit' in request.form:
    firstname=request.form['firstname']
    lastname=request.form['lastname']
    email=request.form['email']
    phone=request.form['phone']
    place=request.form['place']
    housename = request.form['housename']
    pincode = request.form['pincode']
    username=request.form['username']
    password=request.form['password']

    qry="insert into login values(null,'%s','%s','seller')"%(username,password)
    res=insert(qry)

    qry1="insert into seller values(null,'%s','%s','%s','%s','%s','%s','%s','%s')"%(firstname,lastname,email,phone,place,res,housename,pincode)
    insert(qry1)
    return "<script>alert('Submitted successfuly');window.location='/'</script>"
  return render_template('seller.html')


