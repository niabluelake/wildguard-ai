from flask import Flask
from routes.main_routes import main_bp
from routes.risk_routes import risk_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(main_bp)
    app.register_blueprint(risk_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)