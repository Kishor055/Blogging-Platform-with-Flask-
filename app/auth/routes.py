from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.auth.forms import LoginForm, ProfileForm, RegistrationForm
from app.models import Post, User
from app.utils.uploads import save_image_upload

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _safe_next_url(target: str | None) -> bool:
    if not target:
        return False
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Welcome to BlogSphere. Your account is ready.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("You are signed in.", "success")
            next_url = request.args.get("next")
            return redirect(next_url if _safe_next_url(next_url) else url_for("dashboard.index"))
        flash("Email or password is incorrect.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("blog.index"))


@auth_bp.route("/profile/<username>", methods=["GET", "POST"])
def profile(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    form = None
    posts = Post.query.filter_by(author_id=user.id, status="published").order_by(Post.created_at.desc())
    if current_user.is_authenticated and current_user.id == user.id:
        form = ProfileForm(user.id, obj=user)
        if form.validate_on_submit():
            user.username = form.username.data.strip()
            user.bio = form.bio.data.strip()
            try:
                image_name = save_image_upload(form.profile_image.data) if form.profile_image.data and form.profile_image.data.filename else None
            except ValueError as exc:
                form.profile_image.errors.append(str(exc))
                return render_template("auth/profile.html", profile_user=user, posts=posts, form=form)
            if image_name:
                user.profile_image = image_name
            db.session.commit()
            flash("Your profile has been updated.", "success")
            return redirect(url_for("auth.profile", username=user.username))
    return render_template("auth/profile.html", profile_user=user, posts=posts, form=form)
