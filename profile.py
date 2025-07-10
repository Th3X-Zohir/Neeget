from flask import Blueprint, render_template, g, redirect, url_for, request, flash, current_app
from data_manager import DataManager

bp = Blueprint("profile", __name__, url_prefix="/profile")

@bp.before_app_request
def load_logged_in_user():
    user_id = g.user["id"] if g.user else None
    if user_id is None:
        g.user = None
    else:
        g.user = current_app.db.get_by_id("Users", user_id)

@bp.route("/<int:user_id>")
def view(user_id):
    user = current_app.db.get_by_id("Users", user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("index"))

    # Dummy data for user_stats and provider_stats for testing
    user_stats = {
        "total_bookings": 10,
        "pending_bookings": 2,
        "completed_bookings": 8,
        "favorite_services": 5
    }
    provider_stats = {
        "total_services": 3,
        "total_bookings": 15,
        "average_rating": 4.8,
        "total_earnings": 1200,
        "response_rate": 95,
        "completion_rate": 98,
        "satisfaction_rate": 96
    }

    return render_template("profile/view.html", user=user, user_stats=user_stats, provider_stats=provider_stats)

@bp.route("/edit", methods=["GET", "POST"])
def edit():
    if not g.user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # Handle profile update logic here
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.view", user_id=g.user["id"]))

    return render_template("profile/edit.html", user=g.user)


