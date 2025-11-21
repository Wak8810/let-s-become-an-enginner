from src.database import db
from src.models import Statuses

status = {0: "PENDING", 1: "GENERATING", 2: "COMPLETED", 3: "FAILED"}

def init_db_statuses(app):
    with app.app_context():
        for id, value in status.items():
            exist = Statuses.query.get(id)
            if not exist:
                db.session.add(Statuses(id=id, status=value))
            db.session.commit()

def get_status_id(name):
    for key, value in status.items():
        if value == name:
            return key
    raise f'status name error - {str} status doesn\'t exist / raised at "backend/src/status.py"'
