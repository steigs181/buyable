from flask_app.models.class_users import Users
from flask import session

class UserSession:
    def __init__(self):
        self.id=None
        self.user_name="Guest"
        self.logged_on=False
        self.cart=0
        self.seller=False
        self.seller_id=-1
    def check_status(self):
        self.cart=0
        self.seller=False
        if "user_loggedon" in session:
            user=Users.get_userinfo(session['user_email'])
            self.id=user.id
            self.user_name=f"{user.first_name} {user.last_name}"
            self.logged_on=True
            self.seller=Users.is_seller(user.id)
            self.cart=Users.cart_count(user.id);
            if self.seller:
                self.seller_id=Users.get_seller_id(user.id)
            return self;
        self.logged_on=False
        return self;