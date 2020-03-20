from app import create_app, db
from app.models import User
app = create_app()


@app.shell_context_processor
def makeShellContext():
    return {'db': db, 'User': User, 'test':"test"}
