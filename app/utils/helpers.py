import re
from datetime import datetime
from functools import wraps
from pathlib import Path
from uuid import uuid4
from flask import current_app, redirect, session, url_for, flash
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s-]+", "-", value)
    return value.strip("-")


def money(value):
    try:
        return "Rs. {:,.0f}".format(float(value))
    except (TypeError, ValueError):
        return value


def save_images(files):
    saved = []
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    for file in files:
        if not file or not file.filename:
            continue
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        filename = secure_filename(f"{uuid4().hex}.{ext}")
        file.save(upload_folder / filename)
        saved.append(f"uploads/{filename}")
    return saved


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login to continue.", "warning")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped


def now():
    return datetime.utcnow()
