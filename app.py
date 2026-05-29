from flask import Flask
from routes.main_routes import main_bp
from routes.risk_routes import risk_bp
from routes.risk_page_routes import risk_page_bp


def create_app():
    app = Flask(__name__)

    app.json.ensure_ascii = False

    app.register_blueprint(main_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(risk_page_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)