from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db
from app.models import Category, Comment, CommentReport, Post, Tag, User
from app.utils.decorators import admin_required
from app.utils.text import slugify

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/")
@admin_required
def index():
    return render_template(
        "admin/index.html", users=User.query.order_by(User.created_at.desc()).all(),
        posts=Post.query.order_by(Post.created_at.desc()).all(),
        comments=Comment.query.order_by(Comment.created_at.desc()).limit(50).all(),
        reports=CommentReport.query.order_by(CommentReport.created_at.desc()).limit(50).all(),
        categories=Category.query.order_by(Category.name).all(), tags=Tag.query.order_by(Tag.name).all(),
    )


@admin_bp.post("/reports/<int:report_id>/resolve")
@admin_required
def resolve_report(report_id: int):
    report = db.session.get(CommentReport, report_id)
    if report is None:
        abort(404)
    report.status = "reviewed"
    db.session.commit()
    flash("The report has been marked as reviewed.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.post("/taxonomy/<kind>")
@admin_required
def create_taxonomy(kind: str):
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()[:240]
    max_name_length = 80 if kind == "category" else 40
    if kind not in {"category", "tag"} or not name or len(name) > max_name_length:
        flash("Enter a valid category or tag name.", "danger")
        return redirect(url_for("admin.index"))
    model = Category if kind == "category" else Tag
    if model.query.filter(db.func.lower(model.name) == name.lower()).first():
        flash(f"That {kind} already exists.", "warning")
        return redirect(url_for("admin.index"))
    base_slug = slugify(name)
    slug = base_slug
    suffix = 2
    while model.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    values = {"name": name, "slug": slug}
    if kind == "category":
        values["description"] = description
    db.session.add(model(**values))
    db.session.commit()
    flash(f"{kind.title()} created.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.post("/posts/<int:post_id>/toggle")
@admin_required
def toggle_post(post_id: int):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    post.status = "draft" if post.status == "published" else "published"
    db.session.commit()
    flash("Article visibility updated.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.post("/users/<int:user_id>/role")
@admin_required
def toggle_role(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        flash("You cannot change your own administrator role.", "danger")
    else:
        user.role = "author" if user.is_admin else "admin"
        db.session.commit()
        flash("User role updated.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.post("/taxonomy/<kind>/<int:item_id>/delete")
@admin_required
def delete_taxonomy(kind: str, item_id: int):
    model = {"category": Category, "tag": Tag}.get(kind)
    if model is None:
        abort(404)
    item = db.session.get(model, item_id)
    if item is None:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash(f"{kind.title()} removed. Existing articles were kept.", "info")
    return redirect(url_for("admin.index"))


@admin_bp.post("/users/<int:user_id>/delete")
@admin_required
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        flash("You cannot delete your own account from the admin studio.", "danger")
        return redirect(url_for("admin.index"))
    db.session.delete(user)
    db.session.commit()
    flash("Member account and its content have been deleted.", "info")
    return redirect(url_for("admin.index"))
