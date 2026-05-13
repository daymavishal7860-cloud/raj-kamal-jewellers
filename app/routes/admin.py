from bson import ObjectId
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from pymongo import ASCENDING, DESCENDING
from werkzeug.security import check_password_hash
from app.models.db import mongo
from app.utils.helpers import admin_required, now, save_images, slugify

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = None
        if mongo.is_connected():
            user = mongo.db.users.find_one({"email": email, "role": "admin"})
        valid_user = user and check_password_hash(user.get("password_hash", ""), password)
        valid_env_fallback = email == current_app.config["ADMIN_EMAIL"] and password == current_app.config["ADMIN_PASSWORD"]
        if valid_user or valid_env_fallback:
            session["admin_logged_in"] = True
            session["admin_email"] = email
            flash("Welcome back to RajKamal admin.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@admin_required
def dashboard():
    connected = mongo.is_connected()
    stats = {
        "products": mongo.db.products.count_documents({}) if connected else 0,
        "categories": mongo.db.categories.count_documents({}) if connected else 0,
        "orders": mongo.db.orders.count_documents({}) if connected else 0,
        "enquiries": mongo.db.enquiries.count_documents({}) if connected else 0,
    }
    recent_enquiries = list(mongo.db.enquiries.find().sort("created_at", DESCENDING).limit(5)) if connected else []
    return render_template("admin/dashboard.html", stats=stats, recent_enquiries=recent_enquiries, connected=connected)


@admin_bp.route("/products")
@admin_required
def products():
    products_data = list(mongo.db.products.find().sort("created_at", DESCENDING)) if mongo.is_connected() else []
    return render_template("admin/products.html", products=products_data)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def product_new():
    if request.method == "POST":
        return save_product()
    categories = list(mongo.db.categories.find().sort("name", ASCENDING)) if mongo.is_connected() else []
    return render_template("admin/product_form.html", product=None, categories=categories)


@admin_bp.route("/products/<product_id>/edit", methods=["GET", "POST"])
@admin_required
def product_edit(product_id):
    if not mongo.is_connected():
        flash("MongoDB connection required for admin editing.", "warning")
        return redirect(url_for("admin.products"))
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for("admin.products"))
    if request.method == "POST":
        return save_product(product_id, product)
    categories = list(mongo.db.categories.find().sort("name", ASCENDING))
    return render_template("admin/product_form.html", product=product, categories=categories)


def save_product(product_id=None, existing=None):
    if not mongo.is_connected():
        flash("MongoDB connection required for admin editing.", "warning")
        return redirect(url_for("admin.products"))

    images = save_images(request.files.getlist("images"))
    existing_images = existing.get("images", []) if existing else []
    name = request.form.get("name", "").strip()
    data = {
        "name": name,
        "slug": slugify(request.form.get("slug") or name),
        "price": float(request.form.get("price") or 0),
        "category": request.form.get("category"),
        "weight": request.form.get("weight"),
        "making_charges": request.form.get("making_charges"),
        "purity": request.form.get("purity"),
        "stones": request.form.get("stones"),
        "stock": int(request.form.get("stock") or 0),
        "description": request.form.get("description"),
        "trending": bool(request.form.get("trending")),
        "images": existing_images + images,
        "updated_at": now(),
    }
    if product_id:
        mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})
        flash("Product updated.", "success")
    else:
        data["created_at"] = now()
        mongo.db.products.insert_one(data)
        flash("Product added.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<product_id>/delete", methods=["POST"])
@admin_required
def product_delete(product_id):
    if mongo.is_connected():
        mongo.db.products.delete_one({"_id": ObjectId(product_id)})
        flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/categories", methods=["POST"])
@admin_required
def category_new():
    if mongo.is_connected():
        name = request.form.get("name", "").strip()
        if name:
            mongo.db.categories.update_one({"slug": slugify(name)}, {"$set": {"name": name, "slug": slugify(name)}}, upsert=True)
            flash("Category saved.", "success")
    return redirect(request.referrer or url_for("admin.products"))


@admin_bp.route("/banners", methods=["GET", "POST"])
@admin_required
def banners():
    if request.method == "POST":
        if not mongo.is_connected():
            flash("MongoDB connection required.", "warning")
            return redirect(url_for("admin.banners"))
        images = save_images(request.files.getlist("image"))
        banner = {
            "title": request.form.get("title"),
            "subtitle": request.form.get("subtitle"),
            "image": images[0] if images else request.form.get("image_url"),
            "order": int(request.form.get("order") or 1),
            "active": bool(request.form.get("active")),
            "created_at": now(),
        }
        mongo.db.banners.insert_one(banner)
        flash("Banner added.", "success")
        return redirect(url_for("admin.banners"))
    banners_data = list(mongo.db.banners.find().sort("order", ASCENDING)) if mongo.is_connected() else []
    return render_template("admin/banners.html", banners=banners_data)


@admin_bp.route("/banners/<banner_id>/delete", methods=["POST"])
@admin_required
def banner_delete(banner_id):
    if mongo.is_connected():
        mongo.db.banners.delete_one({"_id": ObjectId(banner_id)})
        flash("Banner deleted.", "success")
    return redirect(url_for("admin.banners"))


@admin_bp.route("/orders")
@admin_required
def orders():
    connected = mongo.is_connected()
    orders_data = list(mongo.db.orders.find().sort("created_at", DESCENDING)) if connected else []
    enquiries = list(mongo.db.enquiries.find().sort("created_at", DESCENDING)) if connected else []
    return render_template("admin/orders.html", orders=orders_data, enquiries=enquiries)
