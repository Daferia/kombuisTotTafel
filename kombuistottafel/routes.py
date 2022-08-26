from flask import (
    flash, render_template,
    redirect, session, url_for, request)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from kombuistottafel import app, db, mongo
from kombuistottafel.models import Category, Account, Users


@app.route('/')
@app.route("/home")
def home():

    if "user" not in session:
        username = ""
    else:
        username = Users.query.filter(Users.user_name == session[
                                      "user"]).all()[0]

    return render_template("home.html", username=username)


@app.route("/recipes")
def recipes():
    if "user" not in session:
        username = ""
    else:
        username = Users.query.filter(Users.user_name == session[
                                      "user"]).all()[0]

    recipes = list(mongo.db.recipes.find())
    categories = list(Category.query.order_by(Category.category_name).all())

    return render_template("recipes.html", recipes=recipes,
                           categories=categories, username=username)


@app.route("/view_recipe/<recipe_id>")
def view_recipe(recipe_id):
    if "user" not in session:
        username = ""
    else:
        username = Users.query.filter(Users.user_name == session[
                                      "user"]).all()[0]

    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    categories = list(Category.query.order_by(Category.category_name).all())

    return render_template("view_recipe.html", recipe=recipe,
                           categories=categories, username=username)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if "user" not in session:
        username = ""
        flash("You need to be logged in to add a recipe")
        return redirect(url_for("login"))
    else:
        username = Users.query.filter(Users.user_name == session[
                                      "user"]).all()[0]

    if request.method == "POST":
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "category_id": request.form.get("category_id"),
            "prep_time": request.form.get("prep_time"),
            "cooking_time": request.form.get("cooking_time"),
            "servings": request.form.get("servings"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "image_url": request.form.get("image_url"),
            "added_by": session["user"]

        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe has been Added")
        return redirect(url_for("recipes"))

    categories = list(Category.query.order_by(Category.category_name).all())
    return render_template("add_recipe.html",
                           categories=categories, username=username)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    # using username for nav bar authentication
    if "user" not in session:
        username = ""
    else:
        username = Users.query.filter(Users.user_name == session[
                                      "user"]).all()[0]

    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})

    if "user" not in session or session["user"] != recipe["added_by"]:
        flash("You can only edit your own recipes!")
        return redirect(url_for("view_recipe", recipe_id=recipe_id))

    if request.method == "POST":
        submit = {"$set": {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "category_id": request.form.get("category_id"),
            "prep_time": request.form.get("prep_time"),
            "cooking_time": request.form.get("cooking_time"),
            "servings": request.form.get("servings"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "image_url": request.form.get("image_url"),
            "added_by": session["user"]
        }}
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe has been updated")
        return redirect(url_for("view_recipe", recipe_id=recipe_id))

    categories = list(Category.query.order_by(Category.category_name).all())
    return render_template("edit_recipe.html", recipe=recipe,
                           categories=categories, username=username)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})

    if "user" not in session or session["user"] != recipe["added_by"]:
        flash("You can only delete your own recipes!")
        return redirect(url_for("view_recipe", recipe_id=recipe_id))

    mongo.db.recipes.delete_one({'_id': ObjectId(recipe_id)})
    flash("Recipe has been deleted")
    return redirect(url_for("recipes"))


@app.route("/admin")
def admin():

    if "user" not in session:
        flash("You need to have permission to view this page!")
        return redirect(url_for("login"))

    # using username for nav bar authentication
    username = Users.query.filter(Users.user_name == session["user"]).all()[0]

    categories = list(Category.query.order_by(Category.category_name).all())
    accounts = list(Account.query.order_by(Account.account_type).all())
    usernames = list(Users.query.order_by(Users.user_name).all())

    return render_template("admin.html", categories=categories,
                           accounts=accounts, usernames=usernames,
                           username=username)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():

    if "user" not in session or session["user"] != "admin":
        flash("You dont have permission to add categories!")
        return redirect(url_for("login"))

    if request.method == "POST":
        category = Category(category_name=request.form.get(
                            "category_name").lower())
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("add_category.html")


@app.route("/edit_category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if "user" not in session or session["user"] != "admin":
        flash("You dont have permission to edit categoies!")
        return redirect(url_for("login"))

    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        category.category_name = request.form.get("category_name").lower()
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<int:category_id>")
def delete_category(category_id):
    if "user" not in session or session["user"] != "admin":
        flash("You dont have permission to delete categories!")
        return redirect(url_for("login"))

    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    mongo.db.recipes.delete_many({"category_id": str(category_id)})
    return redirect(url_for("admin"))


@app.route("/add_account_type", methods=["GET", "POST"])
def add_account_type():
    if "user" not in session or session["user"] != "admin":
        flash("You dont have permission to add account types!")
        return redirect(url_for("login"))

    if request.method == "POST":
        account = Account(account_type=request.form.get(
                          "account_type").lower())
        db.session.add(account)
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("add_account.html")


@app.route("/delete_account/<int:account_id>")
def delete_account(account_id):
    if "user" not in session or session["user"] != "admin":
        flash("You dont have permission to delete accounts!")
        return redirect(url_for("login"))

    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    mongo.db.tasks.delete_many({"account_id": str(account_id)})
    return redirect(url_for("admin"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = Users.query.filter(Users.user_name == request.form.get(
                                           "username").lower()).all()

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("login"))

        user = Users(
            user_name=request.form.get("username").lower(),
            password=generate_password_hash(request.form.get("password")),
            account_type="Individual",
        )

        db.session.add(user)
        db.session.commit()

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = Users.query.filter(Users.user_name == request.form.get(
                                            "username").lower()).all()

        if existing_user:
            print(request.form.get("username"))
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user[0].password, request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")).title())
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):

    if session["user"]:
        # find recipes to add for logged in user
        user_recipes = list(mongo.db.recipes.find({"added_by": username}))

        # grab the session user's username from db
        username = Users.query.filter(Users.user_name == session[
                                      "user"]).all()[0]

    return render_template("profile.html",
                           username=username, user_recipes=user_recipes)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_new_user", methods=["GET", "POST"])
def add_new_user():
    accounts = list(Account.query.order_by(
        Account.account_type).all())

    if request.method == "POST":
        # check if username already exists in db
        existing_user = Users.query.filter(Users.user_name == request.form.get(
                                           "username").lower()).all()

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("add_new_user"))

        user = Users(
            user_name=request.form.get("username").lower(),
            password=generate_password_hash(request.form.get("password")),
            account_type=request.form.get("account_type"),
        )

        db.session.add(user)
        db.session.commit()

        flash("Added New User Successful!")
        return redirect(url_for("admin"))

    return render_template("add_new_user.html", accounts=accounts)


@app.route("/edit_user/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    accounts = list(Account.query.order_by(Account.account_type).all())
    user = Users.query.get_or_404(id)
    if request.method == "POST":
        user.user_name = request.form.get("username").lower(),
        user.password = generate_password_hash(request.form.get("password")),
        user.account_type = request.form.get("account_type")

        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("edit_user.html", user=user, accounts=accounts)


@app.route("/delete_user/<int:id>")
def delete_user(id):
    user = Users.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    mongo.db.users.delete_many({"id": str(id)})
    return redirect(url_for("admin"))


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    username = Users.query.filter(Users.user_name == session["user"]).all()[0]
    return render_template("recipes.html", recipes=recipes, username=username)
