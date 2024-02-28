from flask import Flask, render_template, session, redirect, request, flash, url_for
import os
from werkzeug.utils import secure_filename
from flask_app import app
from flask_bcrypt import Bcrypt
import datetime
import random
bcrypt = Bcrypt(app)
from flask_app.models.class_usersession import UserSession
from flask_app.models.class_users import Users
from flask_app.models.class_models import Items
from flask_app.models.class_models import Categories
from flask_app.models.class_sellers import Sellers
from flask_app.models.class_shopping_cart import MyCart

@app.route('/action/category',methods=['POST'])
def action_category():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    action=request.args.get('t')
    print(request.form)
    print("[Action]",action)
    if action=="add":
        valid=Categories.check_valid(request.form)
        if not valid:
            session["prev_name"]=request.form['category_name']
            return redirect("/category/add");
        session["prev_name"]=""
        Categories.save(request.form)
    if action=="edit":
        valid=Categories.check_valid(request.form)
        if not valid:
             return redirect(f"/category/edit?id={request.form['item_id']}");
        Categories.update(request.form)
    return redirect("/sellers#categories");

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_ext(filename):
    f=filename.rsplit('.', 1)[1].lower()
    return f;

@app.route('/action/item',methods=['POST'])
def action_item():
    num=0
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    print(request.form)
    valid=Items.check_valid(request.form)
    action=request.args.get('t')
    print("[Action]",action)
    if action=="add":
        session["prev_name"]=request.form['item_name']
        session["prev_price"]=request.form['item_price']
        session["prev_cat"]=request.form['item_cat']
        session["prev_description"]=request.form['item_desc']
        if 'item_img' not in request.files:
            flash('No file part.',"items")
            return redirect("/item/add")
        file = request.files['item_img']
        if file.filename == '':
            flash("No file was selected.","items")
            return redirect("/item/add")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext=file_ext(filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            if not valid:
                return redirect("/item/add");
            done=0
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f"{num}.{ext}")):
                num+=1
            session["prev_name"]=""
            session["prev_price"]=""
            session["prev_cat"]=""
            session["prev_description"]=""
            data={
            'name': request.form['item_name'],
            'price': request.form['item_price'],
            'img': f"{num}.{ext}",
            'description': request.form['item_desc'],
            'user_id': user.id,
            'category_id': request.form['item_cat']
            }
            Items.save(data)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{num}.{ext}"))
    
    if action=="edit":
        if not valid:
            return redirect(f"/item/edit?id={request.form['item_id']}&action=edit");
        data={
            'id': request.form['item_id'],
            'name': request.form['item_name'],
            'price': request.form['item_price'],
            'img': request.form['item_img_copy'],
            'description': request.form['item_desc'],
            'user_id': user.id,
            'category_id': request.form['item_cat']
            }
        if 'item_img' in request.files:
            file = request.files['item_img']
            if not file.filename == '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    ext=file_ext(filename)
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    done=0
                    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f"{num}.{ext}")):
                        num+=1
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{num}.{ext}"))
                    data['img']=f"{num}.{ext}"
        print("[Writing]",data)
        Items.update(data)
    return redirect("/sellers#products");
    
@app.route('/action/seller',methods=['POST'])
def action_seller():
    num=0
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    action=request.args.get('action')
    print(request.form)
    print("[Action]",action)
    if action=="edit":
        data={
            'brand_name': request.form['brand_name'],
            'brand_desc': request.form['brand_desc'],
            'id': user.seller_id,
            'user_id': user.id
        }
        if len(data['brand_name'])>32:
            flash("Brand Name is too long. Must be 32 characters max.","branding")
            return redirect("/sellers");
        Sellers.update(data)
        flash("Updated Info Successfully!","branding_good")
        print(data)
    return redirect("/sellers");
    
@app.route('/action/cart',methods=['POST'])
def action_cart():
    num=0
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
        
    view_id=request.args.get('item')
    if view_id==None:
        return redirect("/error?t=7")
    if view_id.isdigit():
        view_id=int(view_id)
    else:
        return redirect("/error?t=2")
    item=Items.get_one(view_id)
    if item==None:
        return redirect("/error?t=2")
    num=request.form['item_quanity']
    check_loc=MyCart.check_in_cart(view_id,user.id)
    print("Quantity:",num)
    print("Product ID:",view_id)
    print("User ID:",user.id)
    print("[CHECK IN CART]",check_loc)
    data={
    "item_id": view_id,
    "quanity": num,
    "user_id": user.id
    }
    if check_loc==None:
        MyCart.save(data)
    else:
        MyCart.update(data)
    return redirect("/mycart");