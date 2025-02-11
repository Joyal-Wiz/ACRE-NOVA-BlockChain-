from datetime import datetime
from flask import session, request, render_template, redirect

@seller.route('/chat_seller', methods=['GET', 'POST'])
def chat_seller():
    seller_id = session.get('seller')
    if not seller_id:
        return "<script>alert('Seller not logged in'); window.location='/seller_home'</script>"
    
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
    selected_buyer_id = request.args.get('buyer_id')
    chats = []

    if selected_buyer_id:
        try:
            selected_buyer_id = int(selected_buyer_id)
        except ValueError:
            return "<script>alert('Invalid buyer ID'); window.location='/chat'</script>"

        # Debugging - check the selected_buyer_id
        print(f"Selected Buyer ID: {selected_buyer_id}")
        
        chats_query = f"""
            SELECT sender_id, sender_type, receiver_id, receiver_type, message, date, time
            FROM chat
            WHERE (sender_id = {seller_id} AND receiver_id = {selected_buyer_id})
               OR (sender_id = {selected_buyer_id} AND receiver_id = {seller_id})
            ORDER BY date, time ASC
        """
        chats = select(chats_query)

        # Debugging - check chats
        print(f"Fetched Chats: {chats}")

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            now = datetime.now()
            date, time = now.date(), now.time()
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
            print(f"Message Sent: {message}")
        return redirect(f"/chat_seller?buyer_id={selected_buyer_id}")
    
    return render_template('chat_seller.html', buyers=buyers, chats=chats, sender_id=seller_id)