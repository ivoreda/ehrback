from main import create_app
from famapi.settings.extensions import mail

app = create_app()
mail.init_app(app)


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8000, debug=True)
