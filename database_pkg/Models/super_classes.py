from sqlalchemy.exc import IntegrityError
import sqlalchemy

from ..extensions import db


class Base(db.Model):
    __abstract__ = True

    def add_to_db(self, my_object):
        db.session.add(my_object)
        try:
            db.session.commit()
        except IntegrityError:
            print('Integrity Error')
            db.session.rollback()
        except:
            breakpoint()

    def as_dict(self, my_object):
        return {key: value for key, value in sqlalchemy.inspect(my_object).dict.items() if '_sa_' not in key}

    def remove_from_db(self, my_object):
        db.session.delete(my_object)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            breakpoint()
