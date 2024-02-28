import urllib.parse
from flask import Flask, render_template, session, redirect, request, flash
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

DISALLOW_USER_BUY_OWN=False

#-------------------
# Home Essentials
#-------------------

@app.route('/')
def page_home():
    user=UserSession().check_status()
    items=[]
    cats=Categories.get_all()

    cat_sel=-1
    cat_search=request.args.get('c')
    if not cat_search == None:
        if cat_search.isdigit():
            cat_sel=int(cat_search)

    search=request.args.get('f')
    if search==None:
        search="";
    search_url=urllib.parse.quote(search, safe='')
    
    if search=="":
        if cat_sel>-1:
            items=Items.get_all_by_category(cat_sel)
        else:
            items=Items.get_all()
    else:
        items=Items.get_all_by_search(search,cat_sel)
    print("Sanitize Test:", search_url)
    return render_template("buyable_browse.html",user=user,cats=cats,cat_sel=cat_sel,search=search,search_url=search_url,items=items)

@app.route('/user/login')
def page_login():
    user=UserSession().check_status()
    if user.logged_on:
        return redirect('/user/logout')
    return render_template("buyable_login.html",user=user)

@app.route('/user/logout')
def page_user_logout():
    session.clear();
    return redirect("/user/login");

#-------------------
# Shopping Cart & Seller's Zone
#-------------------

@app.route('/mycart')
def page_cart():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    action=request.args.get('action')
    edit_id=request.args.get('id')
    if action=="clear":
        MyCart.clear(user.id)
        return redirect('/');
    if action=="delete":
        print(edit_id)
        if not edit_id==None:
            MyCart.delete_by_user(edit_id,user.id)
        return redirect('/mycart');
    items=MyCart.get_all_by_user(user.id)
    
    total=MyCart.get_all_by_user_total(user.id);
    total_str='${:,.2f}'.format(total)
    
    if total==0:
        total_str="Free"
    return render_template("buyable_shopping_cart.html",user=user,items=items,total=total_str)

@app.route('/sellers')
def page_sellers():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    action=request.args.get('action')
    if action=="join":
        if not user.seller:
            Users.add_seller(user.id)
        return redirect("/sellers")
    if user.seller:
        items=Items.get_all_by_user(user.id)
        cats=Categories.get_all()
        seller=Sellers.get_one(user.seller_id)
        return render_template("buyable_sellerzone.html",user=user,items=items,cats=cats,seller=seller)
    return render_template("buyable_sellerzone_consumer.html",user=user)

#-------------------
# Add/Edit Pages
#-------------------

@app.route('/category/add')
def page_category_add():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    item={ "name": "" }
    if 'prev_name' in session:
        item["name"]=session["prev_name"]
        session["prev_name"]=""
    return render_template("buyable_categoryform.html",user=user,item=item)

@app.route('/category/edit')
def page_category_edit():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    edit_id=request.args.get('id')
    action=request.args.get('action')
    if edit_id==None:
        return redirect("/error?t=7")
    if edit_id.isdigit():
        edit_id=int(edit_id)
    else:
        return redirect("/error?t=3")
    item={ "name": "", "id": edit_id }
    cat=Categories.get_one(edit_id)
    if cat==None:
        return redirect("/error?t=3")
    if action=="delete":
        Categories.delete(edit_id)
        return redirect("/sellers#categories")
    item['name']=cat.name
    cat_items=Items.get_all_by_category(edit_id)
    return render_template("buyable_categoryform_edit.html",user=user,item=item,cat=cat,items=cat_items)

@app.route('/item/add')
def page_item_add():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    cats=Categories.get_all()
    if not len(cats)>0:
        return redirect("/error?t=6")
    item={ 
    "name": "",
    "price": "",
    "cat": "",
    "image": "",
    "description": ""
    }
    if 'prev_name' in session:
        item["name"]=session["prev_name"]
        session["prev_name"]=""

    if 'prev_price' in session:
        item["price"]=session["prev_price"]
        session["prev_price"]=""

    if 'prev_cat' in session:
        if session['prev_cat'].isdigit():
            item["cat"]=int(session["prev_cat"])
        session["prev_cat"]=""
    
    if 'prev_image' in session:
        item["image"]=session["prev_image"]
        session["prev_image"]=""

    if 'prev_description' in session:
        item["description"]=session["prev_description"]
        session["prev_description"]=""

    return render_template("buyable_itemform.html",user=user,cats=cats,item=item)

@app.route('/item/edit')
def page_item_edit():
    user=UserSession().check_status()
    if not user.logged_on:
        return redirect('/user/login')
    if not user.seller:
        return redirect("/error?t=8")
    cats=Categories.get_all()
    if not len(cats)>0:
        return redirect("/error?t=6")
    
    edit_id=request.args.get('id')
    action=request.args.get('action')
    if edit_id==None or action==None:
        return redirect("/error?t=7")
    if edit_id.isdigit():
        edit_id=int(edit_id)
    else:
        return redirect("/error?t=2")
    
    item={ "name": "", "id": edit_id }
    product=Items.get_one(edit_id)
    
    if product==None:
        return redirect("/error?t=2")
    if product.user_id != user.id:
        return redirect("/error?t=5")
    
    item={
    "id": product.id,
    "name": product.name,
    "price": product.price,
    "cat": product.category_id,
    "image": product.img,
    "desc": product.description
    }
    print(item)
    if action=="delete":
        product.delete(edit_id,user.id)
        return redirect("/sellers#products");
    return render_template("buyable_itemform_edit.html",user=user,cats=cats,item=item)

#-------------------
# View Pages
#-------------------

@app.route('/item/view')
def page_item():
    allow_buy=False
    psst="You must be logged in to purchase."
    user=UserSession().check_status()
    if user.logged_on:
        psst=""
        allow_buy=True
    view_id=request.args.get('id')
    if view_id==None:
        return redirect("/error?t=7")
    if view_id.isdigit():
        view_id=int(view_id)
    else:
        return redirect("/error?t=2")
    item=Items.get_one(view_id)
    if item==None:
        return redirect("/error?t=2")
    if user.logged_on and DISALLOW_USER_BUY_OWN:
        if item.user_id==user.id:
            allow_buy=False
            psst="Oops. Why would you buy something that you are already selling?"
    cat=Categories.get_one(item.category_id);
    author=Users.user_alias(item.user_id);
    return render_template("buyable_item.html",user=user,item=item, allow_buy=allow_buy, psst=psst, cat=cat, author=author);

@app.route('/user/view')
def page_user():
    user=UserSession().check_status()
    view_id=request.args.get('id')
    if view_id==None:
        return redirect("/error?t=7")
    if view_id.isdigit():
        view_id=int(view_id)
    else:
        return redirect("/error?t=1")
    user_data=Users.get_one(view_id)
    if user_data==None:
        return redirect("/error?t=1")
    seller=Users.is_seller(view_id)
    seller_id=-1
    if seller:
        seller_id=Users.get_seller_id(view_id)
        exa=Sellers.get_one(seller_id)
        person={
        "name": Users.user_alias(view_id),
        "desc": exa['description']
        }
        items=Items.get_all_by_user(view_id)
        return render_template("buyable_user.html",user=user,user_data=user_data,person=person,items=items);
    return render_template("buyable_user_nonseller.html",user=user,user_data=user_data);

#-------------------
# ERRORS
#-------------------


@app.errorhandler(404)
def page_404(e):
    user=UserSession().check_status()
    er={
        'title': "404 Not Found",
        'desc': "You are at a strange place. There's actually nothing to see here."
    }
    return render_template("buyable_error.html",user=user,er=er);

@app.errorhandler(405)
def page_405(e):
    user=UserSession().check_status()
    er={
        'title': "405 Not Allowed",
        'desc': "Oops. You aren't supposed to do that."
    }
    return render_template("buyable_error.html",user=user,er=er);

@app.route('/error')
def page_error():
    user=UserSession().check_status()
    er={
        'title': "Error",
        'desc': "Because it's supposed to have more specific messages... This is effectively an error within an error, or maybe you just choose to look at this page personally."
    }
    error=request.args.get('t')
    if error==None:
        return redirect('/')
    num=0
    if error.isdigit():
        num=int(error)
    
    if num==1:
        er['title']="User Not Found";
        er['desc']="Oops, there's no user nor seller here.";
    if num==2:
        er['title']="Product Not Found";
        er['desc']="Oops, there's no product here.";
    if num==3:
        er['title']="Category Not Found";
        er['desc']="Oops, there's no category here.";
    if num==5:
        er['title']="User Error";
        er['desc']="You are trying to edit or delete something that doesn't belong to you.";
    if num==6:
        er['title']="No Categories Found";
        er['desc']="You can't add nor edit a product, if there's no categories present.";
    if num==7:
        er['title']="Missing Parameters";
        er['desc']="Oops, the needed parameters aren't there.";
    if num==8:
        er['title']="Sellers Only";
        er['desc']="Oops, you can't go to this page yet, because you hadn't signed up as a seller.";
    if num==9:
        er['title']="Loading Error";
        er['desc']="Okay, I have no idea how this could happen.";
    return render_template("buyable_error.html",user=user,er=er);