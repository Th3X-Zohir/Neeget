from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from forms import BookingForm, ReviewForm
from auth import login_required
from datetime import datetime
import random
import string

bp = Blueprint("bookings", __name__, url_prefix="/bookings")

def get_db():
    return current_app.db

def generate_otp():
    """Generate a 6-digit OTP"""
    return "".join(random.choices(string.digits, k=6))

def calculate_platform_fee(amount):
    """Calculate platform fee (10% of service price)"""
    return round(amount * 0.10, 2)

@bp.route("/")
@login_required
def list_bookings():
    """List user's bookings"""
    db = get_db()
    
    bookings = []
    if g.user:
        if g.user["role"] == "service_provider":
            # Show bookings for provider's services
            bookings = db.find_by_attribute("Bookings", "provider_id", g.user["id"])
        else:
            # Show user's bookings
            bookings = db.find_by_attribute("Bookings", "user_id", g.user["id"])
    
    # Enrich bookings with service and user information
    for booking in bookings:
        service = db.get_by_id("Services", booking.get("service_id"))
        user = db.get_by_id("Users", booking.get("user_id"))
        provider = db.get_by_id("Users", booking.get("provider_id"))
        
        booking["service"] = service
        booking["user"] = user
        booking["provider"] = provider
    
    return render_template("bookings/list.html", bookings=bookings)

@bp.route("/book/<int:service_id>", methods=["GET", "POST"])
@login_required
def book_service(service_id):
    """Book a service"""
    if g.user["role"] != "user":
        flash("Only users can book services.", "error")
        return redirect(url_for("services.browse"))
    
    db = get_db()
    service = db.get_by_id("Services", service_id)
    
    if not service:
        flash("Service not found.", "error")
        return redirect(url_for("services.browse"))
    
    provider = db.get_by_id("Users", service.get("provider_id"))
    form = BookingForm()
    
    if form.validate_on_submit():
        try:
            # Calculate fees
            service_price = float(service["price"])
            platform_fee = calculate_platform_fee(service_price)
            total_amount = service_price + platform_fee
            
            # Create booking
            booking = db.add("Bookings", {
                "user_id": g.user["id"],
                "service_id": service_id,
                "provider_id": service["provider_id"],
                "booking_status": "pending",
                "booking_date": datetime.now().isoformat(),
                "service_date": form.service_date.data.isoformat(),
                "otp_code": generate_otp()
            })
            
            # Create payment record
            payment = db.add("Payments", {
                "booking_id": booking["id"],
                "payment_method": form.payment_method.data,
                "payment_amount": service_price,
                "platform_fee": platform_fee,
                "total_amount": total_amount,
                "payment_status": "pending"
            })
            
            # Create notification for provider
            db.add("Notifications", {
                "user_id": service["provider_id"],
                "notification_type": "in_app",
                "message": f"New booking request from {g.user['name']} for {service['service_name']}"
            })
            
            flash("Booking request submitted successfully!", "success")
            return redirect(url_for("bookings.detail", booking_id=booking["id"]))
            
        except Exception as e:
            flash(f"Error creating booking: {str(e)}", "error")
    
    return render_template("bookings/book.html", form=form, service=service, provider=provider)

@bp.route("/<int:booking_id>")
@login_required
def detail(booking_id):
    """View booking details"""
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    # Check access permissions
    if g.user["role"] == "user" and booking["user_id"] != g.user["id"]:
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    elif g.user["role"] == "service_provider" and booking["provider_id"] != g.user["id"]:
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    # Get related information
    service = db.get_by_id("Services", booking.get("service_id"))
    user = db.get_by_id("Users", booking.get("user_id"))
    provider = db.get_by_id("Users", booking.get("provider_id"))
    payment = db.find_by_attribute("Payments", "booking_id", booking_id)
    payment = payment[0] if payment else None
    
    # Get chat messages
    messages = db.find_by_attribute("Chat_Messages", "booking_id", booking_id)
    
    booking["service"] = service
    booking["user"] = user
    booking["provider"] = provider
    booking["payment"] = payment
    booking["messages"] = messages
    
    return render_template("bookings/detail.html", booking=booking)

@bp.route("/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept_booking(booking_id):
    """Accept a booking (provider only)"""
    if g.user["role"] != "service_provider":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["provider_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "pending":
        flash("Booking cannot be accepted in its current status.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "accepted"})
        
        # Notify user
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your booking has been accepted by {g.user['name']}"
        })
        
        flash("Booking accepted successfully!", "success")
    except Exception as e:
        flash(f"Error accepting booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject_booking(booking_id):
    """Reject a booking (provider only)"""
    if g.user["role"] != "service_provider":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["provider_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "pending":
        flash("Booking cannot be rejected in its current status.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "rejected"})
        
        # Notify user
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your booking has been rejected by {g.user['name']}"
        })
        
        flash("Booking rejected.", "success")
    except Exception as e:
        flash(f"Error rejecting booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/complete", methods=["POST"])
@login_required
def complete_booking(booking_id):
    """Complete a booking (provider only)"""
    if g.user["role"] != "service_provider":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["provider_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "accepted":
        flash("Booking must be accepted before it can be completed.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "completed"})
        
        # Update payment status
        payments = db.find_by_attribute("Payments", "booking_id", booking_id)
        if payments:
            db.update("Payments", payments[0]["id"], {"payment_status": "completed"})
        
        # Notify user
        db.add("Notifications", {
            "user_id": booking["user_id"],
            "notification_type": "in_app",
            "message": f"Your booking has been completed by {g.user['name']}. Please leave a review!"
        })
        
        flash("Booking marked as completed!", "success")
    except Exception as e:
        flash(f"Error completing booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking (user only)"""
    if g.user["role"] != "user":
        flash("Access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["user_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] not in ["pending", "accepted"]:
        flash("Booking cannot be cancelled in its current status.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    try:
        db.update("Bookings", booking_id, {"booking_status": "cancelled"})
        
        # Notify provider
        db.add("Notifications", {
            "user_id": booking["provider_id"],
            "notification_type": "in_app",
            "message": f"Booking has been cancelled by {g.user['name']}"
        })
        
        flash("Booking cancelled successfully.", "success")
    except Exception as e:
        flash(f"Error cancelling booking: {str(e)}", "error")
    
    return redirect(url_for("bookings.detail", booking_id=booking_id))

@bp.route("/<int:booking_id>/review", methods=["GET", "POST"])
@login_required
def review_booking(booking_id):
    """Leave a review for a completed booking"""
    if g.user["role"] != "user":
        flash("Only users can leave reviews.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    db = get_db()
    booking = db.get_by_id("Bookings", booking_id)
    
    if not booking or booking["user_id"] != g.user["id"]:
        flash("Booking not found or access denied.", "error")
        return redirect(url_for("bookings.list_bookings"))
    
    if booking["booking_status"] != "completed":
        flash("You can only review completed bookings.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    # Check if review already exists
    existing_reviews = db.find_by_attribute("Reviews", "booking_id", booking_id)
    if existing_reviews:
        flash("You have already reviewed this booking.", "error")
        return redirect(url_for("bookings.detail", booking_id=booking_id))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        try:
            db.add("Reviews", {
                "booking_id": booking_id,
                "user_id": g.user["id"],
                "provider_id": booking["provider_id"],
                "rating": form.rating.data,
                "comment": form.comment.data,
                "created_at": datetime.now().isoformat()
            })
            
            flash("Review submitted successfully!", "success")
            return redirect(url_for("bookings.detail", booking_id=booking_id))
        except Exception as e:
            flash(f"Error submitting review: {str(e)}", "error")
    
    service = db.get_by_id("Services", booking.get("service_id"))
    provider = db.get_by_id("Users", booking.get("provider_id"))
    
    return render_template("bookings/review.html", form=form, booking=booking, service=service, provider=provider)



