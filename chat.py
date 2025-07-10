from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from auth import login_required
from datetime import datetime

bp = Blueprint('chat', __name__, url_prefix='/chat')

def get_db():
    return current_app.db

@bp.route('/booking/<int:booking_id>')
@login_required
def booking_chat(booking_id):
    """Chat interface for a specific booking"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('bookings.list_bookings'))
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        flash('Access denied.', 'error')
        return redirect(url_for('bookings.list_bookings'))
    
    # Get chat messages
    messages = db.find_by_attribute('Chat_Messages', 'booking_id', booking_id)
    
    # Sort messages by sent_at
    messages.sort(key=lambda x: x.get('sent_at', ''))
    
    # Enrich messages with sender information
    for message in messages:
        sender = db.get_by_id('Users', message.get('sender_id'))
        message['sender_name'] = sender.get('name') if sender else 'Unknown'
    
    # Get other participant info
    if g.user['id'] == booking['user_id']:
        other_user = db.get_by_id('Users', booking['provider_id'])
    else:
        other_user = db.get_by_id('Users', booking['user_id'])
    
    service = db.get_by_id('Services', booking.get('service_id'))
    
    return render_template('chat/booking_chat.html', 
                         booking=booking, 
                         messages=messages, 
                         other_user=other_user,
                         service=service)

@bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a chat message"""
    booking_id = request.form.get('booking_id', type=int)
    message_content = request.form.get('message_content', '').strip()
    
    if not booking_id or not message_content:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    # Determine receiver
    if g.user['id'] == booking['user_id']:
        receiver_id = booking['provider_id']
    else:
        receiver_id = booking['user_id']
    
    try:
        # Add message
        message = db.add('Chat_Messages', {
            'booking_id': booking_id,
            'sender_id': g.user['id'],
            'receiver_id': receiver_id,
            'message_content': message_content,
            'sent_at': datetime.now().isoformat()
        })
        
        # Create notification for receiver
        db.add('Notifications', {
            'user_id': receiver_id,
            'notification_type': 'in_app',
            'message': f'New message from {g.user["name"]}'
        })
        
        return jsonify({
            'success': True, 
            'message': {
                'id': message['id'],
                'sender_name': g.user['name'],
                'message_content': message_content,
                'sent_at': message['sent_at']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/get_messages/<int:booking_id>')
@login_required
def get_messages(booking_id):
    """Get chat messages for a booking (AJAX endpoint)"""
    db = get_db()
    booking = db.get_by_id('Bookings', booking_id)
    
    if not booking:
        return jsonify({'success': False, 'error': 'Booking not found'})
    
    # Check access permissions
    if g.user['id'] not in [booking['user_id'], booking['provider_id']]:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    # Get messages
    messages = db.find_by_attribute('Chat_Messages', 'booking_id', booking_id)
    
    # Sort messages by sent_at
    messages.sort(key=lambda x: x.get('sent_at', ''))
    
    # Enrich messages with sender information
    for message in messages:
        sender = db.get_by_id('Users', message.get('sender_id'))
        message['sender_name'] = sender.get('name') if sender else 'Unknown'
        message['is_own'] = message['sender_id'] == g.user['id']
    
    return jsonify({'success': True, 'messages': messages})

