from app import create_app
from app.models.db import mongo
from app.models.sample_data import BANNERS, CATEGORIES, PRODUCTS
from app.utils.helpers import now
from werkzeug.security import generate_password_hash


def seed():
    app = create_app()
    with app.app_context():
        if not mongo.is_connected():
            raise RuntimeError("MongoDB is not reachable. Start MongoDB and try again.")

        mongo.db.categories.delete_many({})
        mongo.db.products.delete_many({})
        mongo.db.banners.delete_many({})
        mongo.db.users.delete_many({"email": app.config["ADMIN_EMAIL"]})

        categories = [{**item, "created_at": now()} for item in CATEGORIES]
        products = [{**item, "created_at": now(), "updated_at": now()} for item in PRODUCTS]
        banners = [{**item, "created_at": now()} for item in BANNERS]

        mongo.db.categories.insert_many(categories)
        mongo.db.products.insert_many(products)
        mongo.db.banners.insert_many(banners)
        mongo.db.users.insert_one({
            "email": app.config["ADMIN_EMAIL"],
            "password_hash": generate_password_hash(app.config["ADMIN_PASSWORD"]),
            "role": "admin",
            "created_at": now(),
        })
        mongo.db.products.create_index("slug", unique=True)
        mongo.db.categories.create_index("slug", unique=True)
        mongo.db.users.create_index("email", unique=True)
        print("Seeded RajKamal Jewellers sample data.")


if __name__ == "__main__":
    seed()
