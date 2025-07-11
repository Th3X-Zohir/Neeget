from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, jsonify
from forms import ServiceForm
from auth import login_required
import random
import string

bp = Blueprint('services', __name__, url_prefix='/services')

def get_db():
    return current_app.db

@bp.route('/')
def browse():
    """Browse all services with optional filtering"""
    db = get_db()
    services = db.get_all('Services')
    categories = db.get_all('Service_Categories')
    
    # Get filter parameters
    category_filter = request.args.get('category')
    location_filter = request.args.get('location')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Apply filters
    if category_filter:
        services = [s for s in services if s.get('category_id') == int(category_filter)]
    
    if location_filter:
        services = [s for s in services if location_filter.lower() in s.get('location', '').lower()]
    
    if min_price is not None:
        services = [s for s in services if s.get('price', 0) >= min_price]
    
    if max_price is not None:
        services = [s for s in services if s.get('price', 0) <= max_price]
    
    # Enrich services with category and provider information
    for service in services:
        category = db.get_by_id('Service_Categories', service.get('category_id'))
        provider = db.get_by_id('Users', service.get('provider_id'))
        service['category_name'] = category.get('category_name') if category else 'Unknown'
        service['provider_name'] = provider.get('name') if provider else 'Unknown'
        service['provider_email'] = provider.get('email') if provider else 'Unknown'
    
    return render_template('services/browse.html', services=services, categories=categories)

@bp.route('/<int:service_id>')
def detail(service_id):
    """View service details"""
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.browse'))
    
    # Get category and provider information
    category = db.get_by_id('Service_Categories', service.get('category_id'))
    provider = db.get_by_id('Users', service.get('provider_id'))
    
    # Get reviews for this service
    reviews = db.find_by_attribute('Reviews', 'provider_id', service.get('provider_id'))
    
    service['category_name'] = category.get('category_name') if category else 'Unknown'
    service['provider'] = provider
    
    return render_template('services/detail.html', service=service, reviews=reviews)

@bp.route('/manage')
@login_required
def manage():
    """Manage services for providers"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can manage services.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    services = db.find_by_attribute('Services', 'provider_id', g.user['id'])
    categories = db.get_all('Service_Categories')
    
    # Enrich services with category information
    for service in services:
        category = db.get_by_id('Service_Categories', service.get('category_id'))
        service['category_name'] = category.get('category_name') if category else 'Unknown'
    
    return render_template('services/manage.html', services=services, categories=categories)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new service"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can add services.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    form = ServiceForm()
    
    # Populate category choices
    categories = db.get_all('Service_Categories')
    form.category_id.choices = [(c['id'], c['category_name']) for c in categories]
    
    if form.validate_on_submit():
        try:
            service = db.add('Services', {
                'category_id': form.category_id.data,
                'provider_id': g.user['id'],
                'service_name': form.service_name.data,
                'description': form.description.data,
                'price': float(form.price.data),
                'location': form.location.data
            })
            flash('Service added successfully!', 'success')
            return redirect(url_for('services.manage'))
        except Exception as e:
            flash(f'Error adding service: {str(e)}', 'error')
    
    return render_template('services/add.html', form=form)

@bp.route('/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit(service_id):
    """Edit an existing service"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can edit services.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.manage'))
    
    if service['provider_id'] != g.user['id']:
        flash('Access denied. You can only edit your own services.', 'error')
        return redirect(url_for('services.manage'))
    
    form = ServiceForm(obj=type('obj', (object,), service)())
    
    # Populate category choices
    categories = db.get_all('Service_Categories')
    form.category_id.choices = [(c['id'], c['category_name']) for c in categories]
    
    if form.validate_on_submit():
        try:
            db.update('Services', service_id, {
                'category_id': form.category_id.data,
                'service_name': form.service_name.data,
                'description': form.description.data,
                'price': float(form.price.data),
                'location': form.location.data
            })
            flash('Service updated successfully!', 'success')
            return redirect(url_for('services.manage'))
        except Exception as e:
            flash(f'Error updating service: {str(e)}', 'error')
    
    return render_template('services/edit.html', form=form, service=service)

@bp.route('/delete/<int:service_id>', methods=['POST'])
@login_required
def delete(service_id):
    """Delete a service"""
    if g.user['role'] != 'service_provider':
        flash('Access denied. Only service providers can delete services.', 'error')
        return redirect(url_for('index'))
    
    db = get_db()
    service = db.get_by_id('Services', service_id)
    
    if not service:
        flash('Service not found.', 'error')
        return redirect(url_for('services.manage'))
    
    if service['provider_id'] != g.user['id']:
        flash('Access denied. You can only delete your own services.', 'error')
        return redirect(url_for('services.manage'))
    
    try:
        db.delete('Services', service_id)
        flash('Service deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting service: {str(e)}', 'error')
    
    return redirect(url_for('services.manage'))

@bp.route('/categories')
def categories():
    """List all service categories"""
    db = get_db()
    categories = db.get_all('Service_Categories')
    return render_template('services/categories.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """Add a new service category (admin only)"""
    if g.user['role'] != 'admin':
        flash('Access denied. Only admins can add categories.', 'error')
        return redirect(url_for('services.categories'))
    
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        description = request.form.get('description')
        
        if not category_name:
            flash('Category name is required.', 'error')
        else:
            try:
                db = get_db()
                db.add('Service_Categories', {
                    'category_name': category_name,
                    'description': description
                })
                flash('Category added successfully!', 'success')
                return redirect(url_for('services.categories'))
            except Exception as e:
                flash(f'Error adding category: {str(e)}', 'error')
    
    return render_template('services/add_category.html')

