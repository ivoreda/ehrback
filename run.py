from main import create_app
from famapi.settings.extensions import mail
from famapi.settings.database import Base, engine

app = create_app()
mail.init_app(app)


Base.metadata.create_all(bind=engine)
if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8000, debug=True)
