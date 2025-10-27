from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import Item, User
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Blueprints
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
items = Blueprint('items', __name__)

# Main Routes
@main.route('/')
def index():
    recent_items = Item.query.filter_by(status='open').order_by(Item.created_at.desc()).limit(6).all()
    stats = {
        'lost_items': Item.query.filter_by(item_type='lost', status='open').count(),
        'found_items': Item.query.filter_by(item_type='found', status='open').count(),
        'total_users': User.query.count()
    }
    return render_template('index.html', items=recent_items, stats=stats)

@main.route('/dashboard')
@login_required
def dashboard():
    user_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.created_at.desc()).all()
    return render_template('dashboard.html', items=user_items)

# Authentication Routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, phone=phone)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# Item Management Routes
@items.route('/report', methods=['GET', 'POST'])
@login_required
def report_item():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        location = request.form.get('location')
        date_str = request.form.get('date')
        item_type = request.form.get('type')
        
        try:
            date_lost_found = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('report_item.html')
        
        item = Item(
            title=title,
            description=description,
            category=category,
            location=location,
            date_lost_found=date_lost_found,
            item_type=item_type,
            user_id=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        flash('Item reported successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('report_item.html')

@items.route('/search')
def search_items():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    item_type = request.args.get('type', '')
    
    items_query = Item.query.filter_by(status='open')
    
    if query:
        items_query = items_query.filter(
            db.or_(
                Item.title.contains(query),
                Item.description.contains(query),
                Item.location.contains(query)
            )
        )
    if category:
        items_query = items_query.filter_by(category=category)
    if item_type:
        items_query = items_query.filter_by(item_type=item_type)
    
    items = items_query.order_by(Item.created_at.desc()).all()
    return render_template('search.html', items=items, search_query=query)

@items.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@items.route('/claim/<int:item_id>')
@login_required
def claim_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if item.user_id == current_user.id:
        flash('You cannot claim your own item', 'error')
    elif item.item_type == 'found' and item.status == 'open':
        item.status = 'claimed'
        item.claimed_by = current_user.id
        db.session.commit()
        flash('Item claimed successfully! Please contact the reporter.', 'success')
    else:
        flash('Item cannot be claimed', 'error')
    
    return redirect(url_for('items.item_detail', item_id=item_id))

@items.route('/close/<int:item_id>')
@login_required
def close_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if item.user_id == current_user.id or current_user.is_admin:
        item.status = 'closed'
        db.session.commit()
        flash('Item marked as closed', 'success')
    
    return redirect(url_for('main.dashboard'))

# API Routes
@items.route('/api/items')
def api_items():
    items = Item.query.filter_by(status='open').all()
    result = []
    for item in items:
        result.append({
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'category': item.category,
            'location': item.location,
            'type': item.item_type,
            'date': item.date_lost_found.strftime('%Y-%m-%d'),
            'created_at': item.created_at.strftime('%Y-%m-%d')
        })
    return jsonify(result)