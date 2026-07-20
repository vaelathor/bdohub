from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import argparse
from modules.bartering.app import bartering_bp
from modules.hunting.app import hunting_bp, init_manager
from modules.cp.app import cp_bp
from modules.dashboard.app import dashboard_bp
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.context_processor
def inject_base_path():
    return dict(base_path='/bdohub')


# Registra os Blueprints com prefixos de URL
app.register_blueprint(bartering_bp, url_prefix='/bartering')
app.register_blueprint(hunting_bp, url_prefix='/hunting')
app.register_blueprint(cp_bp, url_prefix='/cp')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="BDO Tools Hub Centralizer")
    parser.add_argument('-t', '--test', action='store_true', help="Ativa o modo de teste para o módulo de Hunting")
    args = parser.parse_args()

    # Inicializa o manager do hunting com o modo de teste se solicitado
    init_manager(test_mode=args.test)

    # Rodando o Hub na porta 8080 como centralizador único
    print("Hub BDO iniciado em http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
