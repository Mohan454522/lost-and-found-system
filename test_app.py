import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

try:
    from app import create_app, db
    from app.models import User, Item
    print("✓ All imports successful!")
    
    # Test database creation
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Test sample data
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        print("✓ Sample user created successfully!")
        
        item = Item(
            title="Test Item",
            description="This is a test item",
            category="Electronics",
            location="Test Location",
            date_lost_found=datetime.now(),
            item_type="lost",
            user_id=user.id
        )
        db.session.add(item)
        db.session.commit()
        print("✓ Sample item created successfully!")
        
        # Clean up
        db.session.delete(item)
        db.session.delete(user)
        db.session.commit()
        print("✓ Test data cleaned up!")
        
    print("\n🎉 ALL TESTS PASSED! Application is working correctly.")
    print("\nNext steps:")
    print("1. Run: python run.py")
    print("2. Open: http://localhost:5000")
    print("3. Register a new account and start using the app!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("1. Make sure you're in the project directory")
    print("2. Run: pip install -r requirements.txt")
    print("3. Check if all files are created properly")
