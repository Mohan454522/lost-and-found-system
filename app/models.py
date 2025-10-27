from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('Item', backref='reporter', lazy=True, foreign_keys='Item.user_id')
    claimed_items = db.relationship('Item', backref='claimer', lazy=True, foreign_keys='Item.claimed_by')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date_lost_found = db.Column(db.DateTime, nullable=False)
    item_type = db.Column(db.String(10), nullable=False)  # 'lost' or 'found'
    status = db.Column(db.String(20), default='open')  # 'open', 'claimed', 'closed'
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    claimed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<Item {self.title}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
