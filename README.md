# RajKamal Jewellers

Modern premium Indian jewellery shop website built with Flask, MongoDB, TailwindCSS, and Jinja2.

## Features

- Luxury mobile-first storefront with sticky navbar, hero carousel, product sections, testimonials, Instagram gallery, WhatsApp button, and Google Maps.
- Product listing with search, category filters, pagination, wishlist, lazy-loaded images, and SEO-friendly slugs.
- Product details with image gallery, hover zoom, specifications, related products, cart and WhatsApp enquiry actions.
- Bridal collection page with cinematic layout and appointment booking.
- About and contact pages with enquiry capture.
- Session-based admin login backed by the `users` collection when MongoDB is available, dashboard metrics, products CRUD, multi-image uploads to `app/static/uploads`, categories, banners, orders, and enquiries.
- MongoDB collections: `users`, `products`, `categories`, `banners`, `enquiries`, `orders`.

## Quick Start

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy environment settings.

```bash
copy .env.example .env
```

4. Start MongoDB locally, then seed sample data.

```bash
python seed_data.py
```

5. Run the app.

```bash
flask --app run.py --debug run
```

Open `http://127.0.0.1:5000`.

## Deploy on Render

1. Push this project to a GitHub repository.
2. Create a MongoDB Atlas cluster and copy your connection string.
3. In Render, create a new Web Service from the GitHub repo.
4. Use these settings:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn run:app
```

5. Add these Render environment variables:

```text
SECRET_KEY=<generate a long random value>
MONGO_URI=<your MongoDB Atlas connection string>
ADMIN_EMAIL=<your admin email>
ADMIN_PASSWORD=<your admin password>
```

6. After the first deploy, open Render Shell and run this once if you want starter data:

```bash
python seed_data.py
```

Do not run `seed_data.py` repeatedly on production unless you want to reset products, categories, banners, and the seeded admin user.

## Admin Login

Default demo credentials are set in `.env.example` and seeded into the `users` collection by `python seed_data.py`.

- Email: `admin@rajkamal.test`
- Password: `admin123`

Change `SECRET_KEY`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` before using this outside development.

## Project Structure

```text
app/
  routes/          Public and admin Flask routes
  templates/       Jinja2 templates
  static/          CSS, JS, uploaded images
  models/          MongoDB connection and sample data
  utils/           Helpers for auth, uploads, slugs
run.py
seed_data.py
requirements.txt
```

## TailwindCSS

The project uses Tailwind CDN for beginner-friendly startup. For production, install Node dependencies and wire a compiled CSS build:

```bash
npm install
npm run tailwind:build
```

Then include `app/static/css/tailwind.css` in `base.html` instead of the CDN script.

## Notes

- If MongoDB is not running, the public site still displays bundled sample data so the UI can be previewed immediately.
- Admin editing requires MongoDB to be connected.
- Replace placeholder images and Google Maps location with real RajKamal Jewellers assets before launch.
