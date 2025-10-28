from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Your app configuration
    app.config['SECRET_KEY'] = 'terraform-production-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost_found.db'
    
    # Your routes
    @app.route('/')
    def home():
        return "Lost & Found System - Hello World!"
    
    return app

app = create_app()

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=5000)