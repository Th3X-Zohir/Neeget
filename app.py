from flask import Flask, render_template, redirect, url_for, g, session
from flask_wtf.csrf import CSRFProtect
from data_manager import DataManager
import auth
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    # Enable CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize DataManager
    app.db = DataManager(app.config["JSON_DATABASE_DIR"])
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    
    import services
    app.register_blueprint(services.bp)
    
    import bookings
    app.register_blueprint(bookings.bp)
    
    import chat
    app.register_blueprint(chat.bp)
    
    import admin
    app.register_blueprint(admin.bp)
    
    import profile
    app.register_blueprint(profile.bp)
    
    @app.route("/")
    def index():
        if g.user and "role" in g.user:
            if g.user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif g.user["role"] == "service_provider":
                return redirect(url_for("provider_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        return render_template("index.html")
    
    @app.route("/user_dashboard")
    def user_dashboard():
        # Dummy data for stats and bookings for testing
        stats = {
            "total_bookings": 10,
            "pending_bookings": 2,
            "completed_bookings": 8,
            "favorite_services": 5
        }
        recommended_services = [
            {"id": 1, "service_name": "Gardening", "provider_name": "Alice Green", "category_name": "Home Services", "price": 50.00},
            {"id": 2, "service_name": "Computer Repair", "provider_name": "Bob Fixit", "category_name": "Tech Services", "price": 75.00}
        ]
        bookings = [
            {"id": 1, "service_name": "House Cleaning", "provider_name": "John Doe", "booking_date": "2025-07-15", "booking_time": "10:00 AM", "status": "pending"},
            {"id": 2, "service_name": "Car Wash", "provider_name": "Jane Smith", "booking_date": "2025-07-10", "booking_time": "02:00 PM", "status": "completed"}
        ]
        return render_template("user_dashboard.html", stats=stats, bookings=bookings, recommended_services=recommended_services)    
    @app.route("/provider_dashboard")
    def provider_dashboard():
        # Dummy data for provider stats, booking requests, and services for testing
        provider_stats = {
            "total_services": 3,
            "total_bookings": 15,
            "average_rating": 4.8,
            "total_earnings": 1200,
            "response_rate": 95,
            "completion_rate": 98,
            "satisfaction_rate": 96
        }
        booking_requests = [
            {"id": 1, "service_name": "Plumbing Repair", "user_name": "Alice Brown", "booking_date": "2025-07-18", "booking_time": "09:00 AM", "status": "pending"},
            {"id": 2, "service_name": "Electrical Wiring", "user_name": "Bob White", "booking_date": "2025-07-16", "booking_time": "01:00 PM", "status": "accepted"}
        ]
        my_services = [
            {"id": 1, "service_name": "Plumbing Services", "category_name": "Home Services", "status": "active", "views": 120, "price": 80.00},
            {"id": 2, "service_name": "Electrical Services", "category_name": "Home Services", "status": "active", "views": 90, "price": 100.00}
        ]
        recent_reviews = [
            {"user_name": "Charlie Green", "rating": 5, "comment": "Great service, very professional!", "created_at": "2025-07-09"},
            {"user_name": "Diana Blue", "rating": 4, "comment": "Good work, but a bit slow.", "created_at": "2025-07-08"}
        ]
        return render_template("provider_dashboard.html", provider_stats=provider_stats, booking_requests=booking_requests, my_services=my_services, recent_reviews=recent_reviews)
    
    @app.route("/admin_dashboard")
    def admin_dashboard():
        return render_template("admin_dashboard.html")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)


