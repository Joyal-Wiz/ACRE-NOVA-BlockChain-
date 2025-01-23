from flask import *
from database import*

seller=Blueprint('seller',__name__)

@seller.route('/seller_home')
def seller_home():
  return render_template('seller_home.html')

@seller.route('/viewprofile_seller')
def view_seller_profile():
    qry = "SELECT * FROM seller where seller_id = '%s'"%(session['seller'])
    sellerProfile = select(qry)
    return render_template("viewprofile_seller.html",sellerProfile=sellerProfile)



@seller.route('/view_plots_seller')
def view_plots_seller():
  data={}
  qry = "SELECT * FROM posts where seller_id = '%s'"%(session['seller'])
  allplots = select(qry)
  if allplots:
    data['view']=allplots
  return render_template('view_plot_seller.html',data=data)


import uuid
@seller.route('/add_plot_sellers',methods=['get','post'])
def add_plot_sellers():
   if 'submit' in request.form:
      post_title =request.form['posttitle']
      description=request.form['description']
      img=request.files['img']
      path='static/plot/'+str(uuid.uuid4())+img.filename
      img.save(path)
      amount=request.form['amount']
      qry="insert into posts values(null,'%s','%s','%s','%s',curdate(),'pending','%s')"%(session['seller'],post_title,description,amount,path)
      insert(qry)
      return "<script>alert('updated successfuly');window.location='/seller_home'</script>"
    
   return render_template('add_plot_seller.html')



import uuid
@seller.route('/edit_profile_seller', methods=['GET', 'POST'])
def edit_profile_seller():
    id = request.args.get('id')
    data = {}
    qry = "SELECT * FROM seller WHERE seller_id = '%s'" % (id)
    res = select(qry)
    data['up'] = res

    if 'submit' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        place = request.form['place']
        housename = request.form['housename']
        pincode = request.form['pincode']
        
        
        # dp aploading 
        dp = request.files.get('dp')
        dp_path = None
        if dp:
            upload_folder = 'static/profile/'
            # uuid Generate a unique file name
            filename = str(uuid.uuid4()) + '.' + dp.filename.split('.')[-1]
            dp_path = upload_folder + filename
            dp.save(dp_path)
        qry = "UPDATE seller SET first_name = '%s', last_name = '%s', email = '%s', phone = '%s', place = '%s', house_name = '%s', pincode = '%s'" % (firstname, lastname, email, phone, place, housename, pincode)
        
        
        # If there's a new profile image, update it too        
        if dp_path:
            qry += ", dp = '%s'" % (dp_path)
        qry += " WHERE seller_id = '%s'" % (id)
        update(qry)
        return "<script>alert('Updated successfully'); window.location='/viewprofile_seller'</script>"
      
    return render_template('edit_profile_seller.html', data=data)


@seller.route('/edit_post_seller', methods = ['GET','POST'])
def edit_post_seller():
    post_id=request.args['id']
    data={}
    qry = "SELECT * FROM posts WHERE post_id = '%s'" % (post_id)
    res= select(qry)
    data['up']=res
    if 'submit' in request.form:
      post_title=request.form['post_title']
      description=request.form['description']
      amount=request.form['amount']
      qry="update posts set post_title = '%s',description = '%s',amount = '%s' WHERE post_id = '%s'" %(post_title,description,amount,post_id)      
      update(qry)
      return "<script>alert('updated successfuly');window.location='/view_plots_seller'</script>"
    return render_template('edit_post_seller.html',data=data)

  
@seller.route('/delete_post_seller', methods=['GET','POST'])
def delete_post_seller():
    post_id = request.args.get('id')  
    qry = "SELECT * FROM posts WHERE post_id = '%s'" % (post_id)
    res = select(qry)
    if res:
      qry = "DELETE FROM posts WHERE post_id = '%s'" % (post_id)
      delete(qry)
      return "<script>alert('Post deleted successfully!');window.location='/view_plots_seller'</script>"
    
    

    
@seller.route('/view_request_seller')
def view_request_seller():
  qry = "SELECT * FROM request where  status != 'rejected'"

  sellerProfile = select(qry)

  if 'action'  in request.args:
    action=request.args['action']
    id=request.args['id']

  else:
    action=None
    
  if action == 'accept':
     qry = "UPDATE request SET status = 'accepted' WHERE request_id = '%s'" %(id)
     update(qry)
  if action == 'reject':
     qry = "UPDATE request SET status = 'rejected' WHERE request_id = '%s'" %(id)
     update(qry)
  return render_template("view_request_seller.html",requests=sellerProfile)










from datetime import datetime
from flask import session, request, render_template, redirect

@seller.route('/chat_seller', methods=['GET', 'POST'])
def chat_seller():
    # Fetch seller_id from the session
    seller_id = session.get('seller')
    if not seller_id:
        return "<script>alert('Seller not logged in'); window.location='/seller_home'</script>"

    # Fetch the list of buyers who have interacted with the seller
    buyers_query = f"""
        SELECT DISTINCT
            b.buyer_id,
            b.first_name,
            b.last_name
        FROM buyer b
        JOIN chat c ON b.buyer_id = CASE
            WHEN c.sender_id != {seller_id} THEN c.sender_id
            ELSE c.receiver_id
        END
        WHERE c.sender_id = {seller_id} OR c.receiver_id = {seller_id}
    """
    buyers = select(buyers_query)

    # Fetch the selected buyer_id from the request arguments
    selected_buyer_id = request.args.get('buyer_id')
    chats = []

    if selected_buyer_id:
        try:
            selected_buyer_id = int(selected_buyer_id)
        except ValueError:
            return "<script>alert('Invalid buyer ID'); window.location='/chat'</script>"

        # Fetch the chat history between the seller and the selected buyer
        chats_query = f"""
            SELECT sender_id, sender_type, receiver_id, receiver_type, message, date, time
            FROM chat
            WHERE (sender_id = {seller_id} AND receiver_id = {selected_buyer_id})
               OR (sender_id = {selected_buyer_id} AND receiver_id = {seller_id})
            ORDER BY date, time ASC
        """
        chats = select(chats_query)

    if request.method == 'POST':
        # Handle sending a new message
        message = request.form.get('message')
        if message:
            now = datetime.now()
            date, time = now.date(), now.time()

            # Insert the message, ensuring no duplicate entries
            insert_query = f"""
                INSERT INTO chat (sender_id, sender_type, receiver_id, receiver_type, message, date, time)
                SELECT {seller_id}, 'seller', {selected_buyer_id}, 'buyer', '{message}', '{date}', '{time}'
                WHERE NOT EXISTS (
                    SELECT 1 FROM chat
                    WHERE sender_id = {seller_id} AND receiver_id = {selected_buyer_id}
                    AND message = '{message}' AND date = '{date}' AND time = '{time}'
                )
            """
            insert(insert_query)
        return redirect(f"/chat_seller?buyer_id={selected_buyer_id}")

    # Render the chat template
    return render_template('chat_seller.html', buyers=buyers, chats=chats, sender_id=seller_id)
