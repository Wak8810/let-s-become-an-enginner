from src.database import db
from src.models import Statuses

def init_db_statuses(app):
    with app.app_context():
        default = {(0, "PENDING"), (1, "GENERATING"), (2, "COMPLETED"), (3, "FAILED")}
        for id, value in default:
            exist = Statuses.query.get(id)
            if not exist:
                db.session.add(Statuses(id=id, status=value))
            db.session.commit()

status={0: "PENDING",1: "GENERATING",2: "COMPLETED",3: "FAILED"}
def get_status_id(str):
    for key,value in status:
        if str==value:
            return key