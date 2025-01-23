from flask import *
from database import *

buyer=Blueprint('buyer',__name__)

@buyer.route('/buyer_home')

def buyer_home():
  return render_template('buyer_home.html')

@buyer.route('/viewprofile_buyer')
def view_buyer_profile():
  qry = "SELECT * FROM buyer where buyer_id='%s'"%(session['buyer'])
  buyerProfile = select(qry)
  return render_template("viewprofile_buyer.html",buyerProfile=buyerProfile)

@buyer.route('/view_posts_buyer')
def view_buyer_posts():
  qry = "SELECT * FROM `posts` INNER JOIN `seller` USING(seller_id)"
  viewposts = select(qry)
  return render_template("viewpost_buyer.html",viewposts=viewposts)

@buyer.route('/edit_profile_buyer', methods = ['GET','POST'])
def edit_profile_buyer():
    id=request.args['id']
    data={}
    qry = "SELECT * FROM buyer WHERE buyer_id = '%s'" % (id)
    res= select(qry)
    data['up']=res

    if 'submit' in request.form:
      firstname=request.form['firstname']
      lastname=request.form['lastname']
      email=request.form['email']
      phone=request.form['phone']
      place=request.form['place']
      housename = request.form['housename']
      pincode = request.form['pincode']
      

      qry="update buyer set first_name = '%s',last_name = '%s',email = '%s',phone = '%s', place='%s',house_name='%s',pincode = '%s' WHERE buyer_id = '%s'" %(firstname,lastname,email,phone,place,housename,pincode,id)
      update(qry)
      return "<script>alert('updated successfuly');window.location='/viewprofile_buyer'</script>"
    return render_template('edit_profile_buyer.html',data=data)

@buyer.route('/change_password_buyer', methods = ['GET','POST'])
def change_password_buyer():
    id=request.args['id']
    data={}
    qry = "SELECT * FROM login WHERE login_id = '%s'" % (id)
    res= select(qry)
    data['up']=res

    if 'submit' in request.form:
      username=request.form['username']
      password=request.form['password']

      qry="update login set username = '%s',password = '%s' WHERE login_id = '%s'" %(username,password,id)
      update(qry)
      return "<script>alert('updated successfuly');window.location='/viewprofile_buyer'</script>"
    return render_template('change_password_buyer.html',data=data)
  


@buyer.route('/send_request', methods=['POST'])
def send_request():
    buyer_id = session.get('buyer') 
    post_id = request.form['post_id']
    if buyer_id and post_id:
        qry = """INSERT INTO request (buyer_id, post_id, date, date_time, status) 
        VALUES ('%s', '%s', CURDATE(),NOW(), 'pending')""" % (buyer_id, post_id)
        insert(qry)
        return "<script>alert('Request sent successfully!');window.location='/view_posts_buyer'</script>"


@buyer.route('/view_interest_status')
def view_interest_status():
    buyer_id = session.get('buyer')  
    qry = "SELECT * FROM request WHERE buyer_id='%s'" % (buyer_id)  
    interest_requests = select(qry)  
    return render_template("view_interest_status_buyer.html", requests=interest_requests)


@buyer.route('/send_complaint', methods=['GET', 'POST'])
def send_complaint():
    if request.method == 'POST':
        complaint = request.form.get('complaint')
        buyer_id = session.get('buyer') 
        qry = "INSERT INTO complaint (sender_id, Complaint, Date) VALUES ('%s', '%s', CURDATE())" % (buyer_id, complaint)
        insert(qry)
        return "<script>alert('Complaint sent successfully!');window.location='/view_reply'</script>"

    return render_template("send_complaint_buyer.html")

  
@buyer.route('/view_reply')
def view_reply():
    buyer_id = session.get('buyer')
    qry = "SELECT * FROM complaint WHERE sender_id='%s'" % (buyer_id)
    complaints = select(qry)
    return render_template("view_reply_buyer.html", complaints=complaints)
  





@buyer.route('/view_user_profile_chat')
def view_user_profile_chat():
    seller_id = request.args.get('id')
    qry = "SELECT * FROM seller WHERE seller_id = '%s'" % (seller_id)
    query_result = select(qry)
    if query_result:
        return render_template("view_user_profile_chat.html", sellerProfile=query_result)


from datetime import datetime

@buyer.route('/chat', methods=['GET', 'POST'])
def buyer_chat():
    sender_id = 1  # Replace with the actual logged-in buyer ID
    sender_type = "buyer"
    receiver_id = request.args.get('receiver_id')  # Seller ID passed from the profile page
    receiver_type = "seller"

    if not receiver_id:
        return "<script>alert('No seller selected'); window.location='/buyer_home'</script>"

    if request.method == 'POST':
        # Send a message
        message = request.form['message']
        now = datetime.now()
        date = now.date()
        time = now.strftime('%H:%M:%S')

        # Insert the message into the database
        query = f"""
            INSERT INTO chat (sender_id, receiver_id, sender_type, receiver_type, message, date, time)
            VALUES ('{sender_id}', '{receiver_id}', '{sender_type}', '{receiver_type}', '{message}', '{date}', '{time}')
        """
        insert(query)

        # Redirect to avoid resending the form data on page reload
        return redirect(url_for('buyer.buyer_chat', receiver_id=receiver_id))

    # Fetch messages between buyer and seller
    query = f"""
        SELECT sender_id, sender_type, receiver_id, receiver_type, message, date, time
        FROM chat
        WHERE (sender_id = {sender_id} AND receiver_id = {receiver_id})
           OR (sender_id = {receiver_id} AND receiver_id = {sender_id})
        ORDER BY date, time ASC
    """
    chats = select(query)

    # Render the chat page with the provided template
    return render_template(
        'chat.html',
        chats=chats,
        sender_id=sender_id,
        receiver_id=receiver_id
    )