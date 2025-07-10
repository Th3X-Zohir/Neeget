from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from forms import ProfileForm, SupportTicketForm
from auth import login_required
from datetime import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile')

def get_db():
    return current_app.db

@bp.route('/')
@login_required
def view():
    """View user profile"""
    return render_template('profile/view.html', user=g.user)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile"""
    form = ProfileForm()
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.name.data = g.user.get('name')
        form.contact_number.data = g.user.get('contact_number')
        form.age.data = g.user.get('age')
        form.profession.data = g.user.get('profession')
        form.address.data = g.user.get('address')
        form.professional_description.data = g.user.get('professional_description')
        form.expertise.data = g.user.get('expertise')
        form.preferred_locations.data = g.user.get('preferred_locations')
        form.portfolio_url.data = g.user.get('portfolio_url')
    
    if form.validate_on_submit():
        try:
            db = get_db()
            updates = {
                'name': form.name.data,
                'contact_number': form.contact_number.data,
                'updated_at': datetime.now().isoformat()
            }
            
            # Add optional fields if provided
            if form.age.data:
                updates['age'] = form.age.data
            if form.profession.data:
                updates['profession'] = form.profession.data
            if form.address.data:
                updates['address'] = form.address.data
            
            # Provider-specific fields
            if g.user['role'] == 'service_provider':
                if form.professional_description.data:
                    updates['professional_description'] = form.professional_description.data
                if form.expertise.data:
                    updates['expertise'] = form.expertise.data
                if form.preferred_locations.data:
                    updates['preferred_locations'] = form.preferred_locations.data
                if form.portfolio_url.data:
                    updates['portfolio_url'] = form.portfolio_url.data
            
            db.update('Users', g.user['id'], updates)
            
            # Update g.user with new data
            g.user.update(updates)
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
    
    return render_template('profile/edit.html', form=form)

@bp.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    db = get_db()
    notifications = db.find_by_attribute('Notifications', 'user_id', g.user['id'])
    
    # Sort by sent_at (newest first)
    notifications.sort(key=lambda x: x.get('sent_at', ''), reverse=True)
    
    return render_template('profile/notifications.html', notifications=notifications)

@bp.route('/notifications/<int:notification_id>/mark_read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    db = get_db()
    notification = db.get_by_id('Notifications', notification_id)
    
    if not notification or notification['user_id'] != g.user['id']:
        flash('Notification not found.', 'error')
        return redirect(url_for('profile.notifications'))
    
    try:
        db.update('Notifications', notification_id, {'is_read': True})
        flash('Notification marked as read.', 'success')
    except Exception as e:
        flash(f'Error updating notification: {str(e)}', 'error')
    
    return redirect(url_for('profile.notifications'))

@bp.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    """Submit a support ticket"""
    form = SupportTicketForm()
    
    if form.validate_on_submit():
        try:
            db = get_db()
            ticket = db.add('Support_Tickets', {
                'user_id': g.user['id'],
                'issue_description': form.issue_description.data,
                'status': 'open',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            flash('Support ticket submitted successfully! We will get back to you soon.', 'success')
            return redirect(url_for('profile.support_tickets'))
        except Exception as e:
            flash(f'Error submitting ticket: {str(e)}', 'error')
    
    return render_template('profile/support.html', form=form)

@bp.route('/support_tickets')
@login_required
def support_tickets():
    """View user's support tickets"""
    db = get_db()
    tickets = db.find_by_attribute('Support_Tickets', 'user_id', g.user['id'])
    
    # Sort by created_at (newest first)
    tickets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('profile/support_tickets.html', tickets=tickets)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required.', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'error')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
        else:
            import bcrypt
            
            # Verify current password
            if not bcrypt.checkpw(current_password.encode('utf-8'), g.user['password_hash'].encode('utf-8')):
                flash('Current password is incorrect.', 'error')
            else:
                try:
                    # Hash new password
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    db = get_db()
                    db.update('Users', g.user['id'], {
                        'password_hash': hashed_password,
                        'updated_at': datetime.now().isoformat()
                    })
                    
                    flash('Password changed successfully!', 'success')
                    return redirect(url_for('profile.view'))
                except Exception as e:
                    flash(f'Error changing password: {str(e)}', 'error')
    
    return render_template('profile/change_password.html')

@bp.route('/reviews')
@login_required
def reviews():
    """View user's reviews (for providers) or reviews given (for users)"""
    db = get_db()
    
    if g.user['role'] == 'service_provider':
        # Show reviews received
        reviews = db.find_by_attribute('Reviews', 'provider_id', g.user['id'])
        title = "Reviews Received"
    else:
        # Show reviews given
        reviews = db.find_by_attribute('Reviews', 'user_id', g.user['id'])
        title = "Reviews Given"
    
    # Enrich reviews with additional information
    for review in reviews:
        if g.user['role'] == 'service_provider':
            user = db.get_by_id('Users', review.get('user_id'))
            review['reviewer'] = user
        else:
            provider = db.get_by_id('Users', review.get('provider_id'))
            review['provider'] = provider
        
        booking = db.get_by_id('Bookings', review.get('booking_id'))
        if booking:
            service = db.get_by_id('Services', booking.get('service_id'))
            review['service'] = service
    
    # Sort by created_at (newest first)
    reviews.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('profile/reviews.html', reviews=reviews, title=title)

