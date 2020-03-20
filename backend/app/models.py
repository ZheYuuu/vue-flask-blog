from app import db
from flask import url_for
from sqlalchemy import DateTime,Integer,String
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime, timedelta
import os


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = dict(
            items=[item.to_dict() for item in resources.items],
            _meta=dict(
                page=page,
                per_page=per_page,
                total_pages=resources.pages,
                total_items=resources.total
            ),
            _links=dict(
                self=url_for(endpoint, page=page, per_page=per_page, **kwargs),
                next=url_for(endpoint, page=page+1, per_page=per_page,
                             **kwargs) if resources.has_next else None,
                prev=url_for(endpoint, page=page-1, per_page=per_page,
                             **kwargs) if resources.has_prev else None,
            )
        )
        return data


class User(PaginatedAPIMixin, db.Model):
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(64), index=True, unique=True)
    email = db.Column(String(120), index=True, unique=True)
    # Do not record raw password
    password_hash = db.Column(String(128))
    token = db.Column(String(32), index=True, unique=True)
    token_expiration = db.Column(DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, includeEmail=False):
        data = dict(
            id=self.id,
            username=self.username,
            _link={
                'self': url_for('api.get_user', id=self.id)
            }
        )
        if includeEmail:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False, **kwargs):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now+timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow()-timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
