from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from .routes.planner import bp as planner_bp
    from .routes.quotes import bp as quotes_bp
    from .routes.cost import bp as cost_bp
    app.register_blueprint(planner_bp, url_prefix="/planner")
    app.register_blueprint(quotes_bp,  url_prefix="/quotes")
    app.register_blueprint(cost_bp,    url_prefix="/cost")

    @app.get("/health")
    def health(): return {"ok": True}
    return app