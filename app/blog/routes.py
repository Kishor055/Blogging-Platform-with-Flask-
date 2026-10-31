import bleach
import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from xml.etree import ElementTree
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Blueprint, Response, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blog.forms import CommentForm, PostForm
from app.models import ArticleView, Bookmark, Category, Post, PostLike, PostRevision, Tag
from app.utils.text import slugify
from app.utils.notifications import create_notification
from app.utils.uploads import save_image_upload

blog_bp = Blueprint("blog", __name__)
ALLOWED_RICH_TEXT_TAGS = [
    "p", "br", "strong", "b", "em", "i", "u", "s", "blockquote", "h1", "h2", "h3",
    "ol", "ul", "li", "a", "pre", "code", "img",
]


def _allowed_rich_text_attribute(tag: str, name: str, value: str) -> bool:
    if tag == "a" and name in {"href", "title"}:
        return True
    return tag == "img" and name in {"src", "alt", "title"} and (
        name != "src" or value.startswith("/static/uploads/")
    )


def _sanitize_rich_text(content: str) -> str:
    return bleach.clean(
        content,
        tags=ALLOWED_RICH_TEXT_TAGS,
        attributes=_allowed_rich_text_attribute,
        protocols={"http", "https", "mailto"},
        strip=True,
    )


def _unique_slug(title: str, post_id: int | None = None) -> str:
    base = slugify(title)[:200]
    candidate = base
    suffix = 2
    while True:
        query = Post.query.filter_by(slug=candidate)
        if post_id:
            query = query.filter(Post.id != post_id)
        if query.first() is None:
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1


def _save_image(upload):
    return save_image_upload(upload)


def _article_form(form):
    form.set_choices(Category.query.order_by(Category.name).all(), Tag.query.order_by(Tag.name).all())


def _schedule_values(form):
    if form.status.data != "scheduled":
        return None, None
    try:
        local_time = datetime.strptime(form.scheduled_local.data or "", "%Y-%m-%dT%H:%M")
    except ValueError:
        form.scheduled_local.errors.append("Choose a valid date and time for scheduled publishing.")
        return None, None
    timezone_name = (form.schedule_timezone.data or "").strip()
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        form.schedule_timezone.errors.append("Enter a valid timezone, such as Europe/London or America/New_York.")
        return None, None
    local_aware = local_time.replace(tzinfo=zone)
    scheduled_at = local_aware.astimezone(timezone.utc)
    if scheduled_at.astimezone(zone).replace(tzinfo=None) != local_time:
        form.scheduled_local.errors.append("That local time does not exist in the selected timezone.")
        return None, None
    if scheduled_at <= datetime.now(timezone.utc):
        form.scheduled_local.errors.append("Choose a time in the future.")
        return None, None
    return scheduled_at, timezone_name


def _record_article_view(post):
    visitor_id = request.cookies.get("blogsphere_visitor")
    should_set_cookie = not visitor_id or len(visitor_id) > 128
    if should_set_cookie:
        visitor_id = secrets.token_urlsafe(32)
    visitor_key = hmac.new(
        current_app.secret_key.encode(), visitor_id.encode(), hashlib.sha256
    ).hexdigest()
    viewed_on = datetime.now(timezone.utc).date()
    if ArticleView.query.filter_by(post_id=post.id, viewed_on=viewed_on, visitor_key=visitor_key).first() is None:
        try:
            with db.session.begin_nested():
                db.session.add(ArticleView(post_id=post.id, viewed_on=viewed_on, visitor_key=visitor_key))
                db.session.flush()
        except IntegrityError as error:
            constraint_name = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
            sqlite_duplicate = (
                "UNIQUE constraint failed: article_view.post_id, article_view.viewed_on, "
                "article_view.visitor_key"
            )
            if constraint_name != "uq_article_view_daily_visitor" and sqlite_duplicate not in str(error.orig):
                raise
        else:
            db.session.commit()
    return visitor_id if should_set_cookie else None


def _can_manage(post: Post) -> bool:
    return current_user.is_authenticated and (current_user.is_admin or post.author_id == current_user.id)


@blog_bp.get("/")
def index():
    return _listing()


@blog_bp.get("/articles")
def articles():
    return _listing()


def _listing(category_slug=None, tag_slug=None):
    query = Post.query.filter_by(status="published")
    search = request.args.get("q", "").strip()[:100]
    category = Category.query.filter_by(slug=category_slug).first() if category_slug else None
    tag = Tag.query.filter_by(slug=tag_slug).first() if tag_slug else None
    if category_slug and category is None:
        abort(404)
    if tag_slug and tag is None:
        abort(404)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Post.title.ilike(pattern), Post.content.ilike(pattern)))
    if category:
        query = query.filter(Post.category_id == category.id)
    if tag:
        query = query.filter(Post.tags.any(Tag.id == tag.id))
    selected_category = request.args.get("category", type=int)
    selected_tag = request.args.get("tag", type=int)
    if selected_category:
        query = query.filter(Post.category_id == selected_category)
    if selected_tag:
        query = query.filter(Post.tags.any(Tag.id == selected_tag))
    sort = request.args.get("sort", "newest")
    ordering = Post.created_at.asc() if sort == "oldest" else Post.created_at.desc()
    pagination = query.order_by(ordering).paginate(
        page=request.args.get("page", 1, type=int), per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    return render_template(
        "blog/index.html", pagination=pagination, search=search, categories=Category.query.order_by(Category.name),
        tags=Tag.query.order_by(Tag.name), selected_category=selected_category, selected_tag=selected_tag,
        category=category, tag=tag, sort=sort,
    )


@blog_bp.get("/category/<slug>")
def category(slug: str):
    return _listing(category_slug=slug)


@blog_bp.get("/tag/<slug>")
def tag(slug: str):
    return _listing(tag_slug=slug)


@blog_bp.get("/sitemap.xml")
def sitemap():
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ElementTree.register_namespace("", namespace)
    root = ElementTree.Element(f"{{{namespace}}}urlset")
    for post in Post.query.filter_by(status="published").order_by(Post.updated_at.desc()).all():
        item = ElementTree.SubElement(root, f"{{{namespace}}}url")
        ElementTree.SubElement(item, f"{{{namespace}}}loc").text = url_for(
            "blog.detail", slug=post.slug, _external=True
        )
        ElementTree.SubElement(item, f"{{{namespace}}}lastmod").text = post.updated_at.date().isoformat()
    return Response(
        ElementTree.tostring(root, encoding="utf-8", xml_declaration=True),
        mimetype="application/xml",
    )


@blog_bp.get("/robots.txt")
def robots():
    sitemap_url = url_for("blog.sitemap", _external=True)
    return Response(f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n", mimetype="text/plain")


@blog_bp.get("/feed.xml")
def feed():
    root = ElementTree.Element("rss", {"version": "2.0"})
    channel = ElementTree.SubElement(root, "channel")
    ElementTree.SubElement(channel, "title").text = "BlogSphere"
    ElementTree.SubElement(channel, "link").text = url_for("blog.index", _external=True)
    ElementTree.SubElement(channel, "description").text = "Thoughtful stories from independent writers."
    for post in Post.query.filter_by(status="published").order_by(Post.created_at.desc()).limit(50):
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = post.title
        ElementTree.SubElement(item, "link").text = url_for("blog.detail", slug=post.slug, _external=True)
        ElementTree.SubElement(item, "guid").text = url_for("blog.detail", slug=post.slug, _external=True)
        ElementTree.SubElement(item, "description").text = post.excerpt
        ElementTree.SubElement(item, "pubDate").text = post.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return Response(ElementTree.tostring(root, encoding="utf-8", xml_declaration=True), mimetype="application/rss+xml")


@blog_bp.route("/article/<slug>", methods=["GET", "POST"])
def detail(slug: str):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not post.is_published and not _can_manage(post):
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))
        from app.models import Comment

        db.session.add(Comment(content=form.content.data.strip(), author=current_user, post=post))
        create_notification(
            post.author_id,
            "comment",
            f"{current_user.username} commented on your article.",
            actor_id=current_user.id,
            post_id=post.id,
        )
        db.session.commit()
        flash("Your comment has been added.", "success")
        return redirect(url_for("blog.detail", slug=post.slug) + "#comments")
    visitor_id = _record_article_view(post) if post.is_published else None
    response = current_app.make_response(
        render_template(
            "blog/detail.html",
            post=post,
            form=form,
            liked=(
                PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None
                if current_user.is_authenticated else False
            ),
            bookmarked=(
                Bookmark.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None
                if current_user.is_authenticated else False
            ),
        )
    )
    if visitor_id:
        response.set_cookie(
            "blogsphere_visitor",
            visitor_id,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            secure=current_app.config.get("SESSION_COOKIE_SECURE", False),
            samesite="Lax",
        )
    return response


@blog_bp.route("/article/new", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()
    _article_form(form)
    if form.validate_on_submit():
        scheduled_at, schedule_timezone = _schedule_values(form)
        if form.category_id.data and not db.session.get(Category, form.category_id.data):
            form.category_id.errors.append("Choose a valid category.")
        if any(not db.session.get(Tag, tag_id) for tag_id in form.tag_ids.data):
            form.tag_ids.errors.append("Choose valid tags.")
        if form.errors:
            return render_template("blog/editor.html", form=form, heading="Write an article")
        try:
            image_name = _save_image(form.featured_image.data)
        except ValueError as error:
            form.featured_image.errors.append(str(error))
            return render_template("blog/editor.html", form=form, heading="Write an article")
        post = Post(
            title=form.title.data.strip(),
            slug=_unique_slug(form.title.data),
            excerpt=form.excerpt.data.strip() or "",
            content=_sanitize_rich_text(form.content.data),
            status=form.status.data,
            scheduled_at=scheduled_at,
            schedule_timezone=schedule_timezone,
            author=current_user,
            category=db.session.get(Category, form.category_id.data) if form.category_id.data else None,
            tags=[db.session.get(Tag, tag_id) for tag_id in form.tag_ids.data],
            featured_image=image_name,
        )
        db.session.add(post)
        db.session.commit()
        flash("Your article has been saved.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("blog/editor.html", form=form, heading="Write an article")


@blog_bp.post("/article/images")
@login_required
def upload_inline_image():
    upload = request.files.get("image")
    if upload is None:
        return jsonify(error="Choose an image to upload."), 400
    try:
        image_name = _save_image(upload)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    return jsonify(url=url_for("static", filename=f"uploads/{image_name}")), 201


@blog_bp.route("/article/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug: str):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not _can_manage(post):
        abort(403)
    form = PostForm(obj=post)
    _article_form(form)
    if request.method == "GET":
        form.category_id.data = post.category_id or 0
        form.tag_ids.data = [item.id for item in post.tags]
        form.schedule_timezone.data = post.schedule_timezone or "UTC"
        if post.scheduled_at:
            scheduled_at = post.scheduled_at
            if scheduled_at.tzinfo is None:
                scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
            form.scheduled_local.data = scheduled_at.astimezone(
                ZoneInfo(post.schedule_timezone or "UTC")
            ).strftime("%Y-%m-%dT%H:%M")
    if form.validate_on_submit():
        scheduled_at, schedule_timezone = _schedule_values(form)
        if form.category_id.data and not db.session.get(Category, form.category_id.data):
            form.category_id.errors.append("Choose a valid category.")
        if any(not db.session.get(Tag, tag_id) for tag_id in form.tag_ids.data):
            form.tag_ids.errors.append("Choose valid tags.")
        if form.errors:
            return render_template("blog/editor.html", form=form, heading="Edit article", post=post)
        try:
            image_name = _save_image(form.featured_image.data)
        except ValueError as error:
            form.featured_image.errors.append(str(error))
            return render_template("blog/editor.html", form=form, heading="Edit article", post=post)
        new_title = form.title.data.strip()
        new_excerpt = form.excerpt.data.strip() or ""
        new_content = _sanitize_rich_text(form.content.data)
        content_changed = (
            post.title != new_title or post.excerpt != new_excerpt or post.content != new_content
        )
        if content_changed:
            db.session.add(
                PostRevision(
                    post=post,
                    editor=current_user,
                    title=post.title,
                    excerpt=post.excerpt,
                    content=post.content,
                )
            )
        post.title = new_title
        post.slug = _unique_slug(post.title, post.id)
        post.excerpt = new_excerpt
        post.content = new_content
        post.status = form.status.data
        post.category = db.session.get(Category, form.category_id.data) if form.category_id.data else None
        post.tags = [db.session.get(Tag, tag_id) for tag_id in form.tag_ids.data]
        if image_name:
            post.featured_image = image_name
        post.scheduled_at = scheduled_at
        post.schedule_timezone = schedule_timezone
        db.session.commit()
        flash("Your article has been updated.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("blog/editor.html", form=form, heading="Edit article", post=post)


@blog_bp.get("/article/<slug>/revisions")
@login_required
def revisions(slug: str):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not _can_manage(post):
        abort(403)
    return render_template("blog/revisions.html", post=post)


@blog_bp.post("/article/<slug>/revisions/<int:revision_id>/restore")
@login_required
def restore_revision(slug: str, revision_id: int):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not _can_manage(post):
        abort(403)
    revision = db.session.get(PostRevision, revision_id)
    if revision is None or revision.post_id != post.id:
        abort(404)
    db.session.add(
        PostRevision(
            post=post,
            editor=current_user,
            title=post.title,
            excerpt=post.excerpt,
            content=post.content,
        )
    )
    post.title = revision.title
    post.slug = _unique_slug(revision.title, post.id)
    post.excerpt = revision.excerpt
    post.content = _sanitize_rich_text(revision.content)
    db.session.commit()
    flash("The selected revision has been restored.", "success")
    return redirect(url_for("blog.edit", slug=post.slug))


@blog_bp.post("/article/<slug>/like")
@login_required
def toggle_like(slug: str):
    post = Post.query.filter_by(slug=slug, status="published").first_or_404()
    like = PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
        message = "You removed your like."
    else:
        db.session.add(PostLike(user_id=current_user.id, post_id=post.id))
        message = "You liked this article."
    db.session.commit()
    flash(message, "success")
    return redirect(url_for("blog.detail", slug=post.slug))


@blog_bp.post("/article/<slug>/bookmark")
@login_required
def toggle_bookmark(slug: str):
    post = Post.query.filter_by(slug=slug, status="published").first_or_404()
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if bookmark:
        db.session.delete(bookmark)
        message = "Article removed from your reading list."
    else:
        db.session.add(Bookmark(user_id=current_user.id, post_id=post.id))
        message = "Article saved to your reading list."
    db.session.commit()
    flash(message, "success")
    return redirect(url_for("blog.detail", slug=post.slug))


@blog_bp.get("/bookmarks")
@login_required
def bookmarks():
    saved_posts = (
        Post.query.join(Bookmark, Bookmark.post_id == Post.id)
        .filter(Bookmark.user_id == current_user.id, Post.status == "published")
        .order_by(Bookmark.created_at.desc())
        .all()
    )
    return render_template("blog/bookmarks.html", posts=saved_posts)


@blog_bp.post("/article/<slug>/delete")
@login_required
def delete(slug: str):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not _can_manage(post):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("The article has been deleted.", "info")
    return redirect(url_for("dashboard.index"))
