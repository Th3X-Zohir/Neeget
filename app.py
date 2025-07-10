from flask import Flask, render_template, redirect, url_for, g, session
from flask_wtf.csrf import CSRFProtect
from data_manager import DataManager
import auth
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Enable CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize DataManager
    app.db = DataManager(app.config['JSON_DATABASE_DIR'])
    
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
    
    @app.route('/')
    def index():
        if g.user:
            if g.user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif g.user['role'] == 'service_provider':
                return redirect(url_for('provider_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        return render_template('index.html')
    
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
    @app.route('/provider_dashboard')
    def provider_dashboard():
        return render_template('provider_dashboard.html')
    
    @app.route('/admin_dashboard')
    def admin_dashboard():
        return render_template('admin_dashboard.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)