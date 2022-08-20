from kombuistottafel import db


class Category(db.Model):
    # schema for the Category model
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(25), unique=True, nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return self.category_name


class Account(db.Model):
    # schema for the user type model
    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return self.user_type


class Users(db.Model):
    # schema for the Task model
    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(10), nullable=False)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(260), nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return self.user_name