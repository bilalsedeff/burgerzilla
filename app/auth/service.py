from datetime import datetime
from email import message
from flask import current_app
from flask_jwt_extended import create_access_token

from app import db
from app.utils import message, err_resp, internal_err_resp
from app.models.users import User
from app.models.schemas import CustomerSchema, RestaurantSchema

customer_schema = CustomerSchema()
restaurant_schema = RestaurantSchema()


class AuthService:
    @staticmethod
    def login(data):
        email = data.get('email')
        password = data.get('password')
        try:
            if not (user := User.query.filter_by(email=email).first()):
                return err_resp('Email herhangi bir hesapla uyuşmadı', "email_404", 404)
            elif user and user.verify_password(password):
                if user['role'] == 'customer':
                    user_info = customer_schema.dump(user)
                    access_token = create_access_token(identity=user.id)
                    resp = message('True', 'Kullanıcı girişi başarılı')
                    resp['access_token'] = access_token
                    resp['user'] = user_info
                    return resp, 200
                elif user['role'] == 'restaurant':
                    user_info = restaurant_schema.dump(user)
                    access_token = create_access_token(identity=user.id)
                    resp = message('True', 'Restoran girişi başarılı')
                    resp['access_token'] = access_token
                    resp['user'] = user_info
                    return resp, 200
            return err_resp('Email veya şifre hatalı', "email_password_404", 404)

        except Exception as e:
            current_app.logger.error(e)
            return internal_err_resp()

    @staticmethod
    def register(data):
        email = data.get('email')
        username = data.get('username')
        name = data.get('name')
        password = data.get('password')
        role = data.get('role')
        if role == 'restaurant':
            restaurant_name = data.get('restaurant_name')
        if User.query.filter_by(email=email).first():
            return err_resp('Bu email adresi kullanılıyor', "email_409", 409)
        elif User.query.filter_by(username=username).first():
            return err_resp('Bu kullanıcı adı kullanılıyor', "username_409", 409)
        try:
            if role == 'customer':
                user = User(email=email, username=username, name=name, password=password, role=role)
                db.session.add(user)
                db.session.commit()
                user_info = customer_schema.dump(user)
                access_token = create_access_token(identity=user.id)
                resp = message('True', 'Kullanıcı kayıt işlemi başarılı')
                resp['access_token'] = access_token
                resp['user'] = user_info
                return resp, 200
            elif role == 'restaurant':
                user = User(email=email, username=username, name=name, password=password, role=role,
                            restaurant_name=restaurant_name)
                db.session.add(user)
                db.session.commit()
                user_info = restaurant_schema.dump(user)
                access_token = create_access_token(identity=user.id)
                resp = message('True', 'Restoran kayıt işlemi başarılı')
                resp['access_token'] = access_token
                resp['user'] = user_info
                return resp, 200
        except Exception as e:
            current_app.logger.error(e)
            return internal_err_resp()
