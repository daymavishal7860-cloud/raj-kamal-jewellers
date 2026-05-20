from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from pymongo import DESCENDING
from app.models.db import mongo
from app.models.sample_data import BANNERS, CATEGORIES, PRODUCTS
from app.utils.helpers import money, now

public_bp = Blueprint("public", __name__)
public_bp.add_app_template_filter(money, "money")


def collection_or_sample(collection, sample):
    if mongo.is_connected() and mongo.db[collection].count_documents({}) > 0:
        return list(mongo.db[collection].find())
    return sample


@public_bp.route("/")
def home():
    banners = collection_or_sample("banners", BANNERS)
    products = collection_or_sample("products", PRODUCTS)
    categories = collection_or_sample("categories", CATEGORIES)
    featured_category_names = {"Gold Jewellery", "Bridal Collections", "Silver Jewellery"}
    categories = [category for category in categories if category.get("name") in featured_category_names]
    trending = [p for p in products if p.get("trending")][:8]
    return render_template("public/home.html", banners=banners, products=products, trending=trending, categories=categories)


@public_bp.route("/collections")
def products():
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 8
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    products_data = collection_or_sample("products", PRODUCTS)
    if search:
        products_data = [p for p in products_data if search.lower() in p.get("name", "").lower()]
    if category:
        products_data = [p for p in products_data if p.get("category") == category]

    total = len(products_data)
    start = (page - 1) * per_page
    paginated = products_data[start:start + per_page]
    categories = collection_or_sample("categories", CATEGORIES)
    return render_template("public/products.html", products=paginated, categories=categories, page=page, total=total, per_page=per_page, search=search, selected_category=category)


@public_bp.route("/collections/<slug>")
def product_detail(slug):
    products_data = collection_or_sample("products", PRODUCTS)
    product = next((p for p in products_data if p.get("slug") == slug), None)
    if not product and mongo.is_connected():
        product = mongo.db.products.find_one({"slug": slug})
    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for("public.products"))

    viewed = session.get("recently_viewed", [])
    viewed = [item for item in viewed if item != slug]
    session["recently_viewed"] = [slug] + viewed[:5]

    related = [p for p in products_data if p.get("category") == product.get("category") and p.get("slug") != slug][:4]
    recent_slugs = [item for item in session.get("recently_viewed", []) if item != slug]
    recent_products = [p for p in products_data if p.get("slug") in recent_slugs][:4]
    return render_template("public/product_detail.html", product=product, related=related, recent_products=recent_products)


@public_bp.route("/bridal")
def bridal():
    products_data = collection_or_sample("products", PRODUCTS)
    bridal_products = [p for p in products_data if "bridal" in p.get("category", "").lower() or "wedding" in p.get("category", "").lower()]
    return render_template("public/bridal.html", products=bridal_products)


@public_bp.route("/gold")
def gold():
    return redirect(url_for("public.products", category="Gold Jewellery"))


@public_bp.route("/silver")
def silver():
    return redirect(url_for("public.products", category="Silver Jewellery"))


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        enquiry = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "message": request.form.get("message"),
            "created_at": now(),
            "status": "new",
        }
        if mongo.is_connected():
            mongo.db.enquiries.insert_one(enquiry)
        flash("Thank you. Our jewellery consultant will contact you soon.", "success")
        return redirect(url_for("public.contact"))
    return render_template("public/contact.html")


@public_bp.route("/wishlist/toggle/<slug>", methods=["POST"])
def toggle_wishlist(slug):
    wishlist = set(session.get("wishlist", []))
    if slug in wishlist:
        wishlist.remove(slug)
        message = "Removed from wishlist."
    else:
        wishlist.add(slug)
        message = "Added to wishlist."
    session["wishlist"] = list(wishlist)
    flash(message, "success")
    return redirect(request.referrer or url_for("public.products"))


@public_bp.route("/product-enquiry/<slug>", methods=["POST"])
def product_enquiry(slug):
    products_data = collection_or_sample("products", PRODUCTS)
    product = next((p for p in products_data if p.get("slug") == slug), None)
    if not product and mongo.is_connected():
        product = mongo.db.products.find_one({"slug": slug})
    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for("public.products"))

    enquiry = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "message": request.form.get("message"),
        "product_slug": slug,
        "product_name": product.get("name"),
        "source": "product_detail",
        "created_at": now(),
        "status": "new",
    }
    if mongo.is_connected():
        mongo.db.enquiries.insert_one(enquiry)
    flash("Product enquiry sent. Our team will contact you soon.", "success")
    return redirect(url_for("public.product_detail", slug=slug))


@public_bp.route("/book-appointment", methods=["POST"])
def book_appointment():
    booking = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone"),
        "date": request.form.get("date"),
        "service": request.form.get("service", "Bridal consultation"),
        "created_at": now(),
        "status": "new",
    }
    if mongo.is_connected():
        mongo.db.orders.insert_one(booking)
    flash("Appointment request received.", "success")
    return redirect(url_for("public.bridal"))
