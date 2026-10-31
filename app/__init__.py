import os
from datetime import datetime
from pathlib import Path

import click
from flask import Flask, render_template
from sqlalchemy import or_

from config import config_by_name
from app.extensions import csrf, db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    selected_config = config_by_name[config_name or os.getenv("APP_ENV", "development")]
    if selected_config is config_by_name["production"]:
        selected_config.validate()
    app.config.from_object(selected_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import Category, Notification, Tag, User
    from app.auth.routes import auth_bp
    from app.blog.routes import blog_bp
    from app.comments.routes import comments_bp
    from app.dashboard.routes import dashboard_bp
    from app.admin.routes import admin_bp
    from app.notifications.routes import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option()
    def create_admin(username: str, email: str, password: str):
        normalized_username = username.strip()
        normalized_email = email.lower().strip()
        if User.query.filter(or_(db.func.lower(User.username) == normalized_username.lower(), db.func.lower(User.email) == normalized_email)).first():
            raise click.ClickException("A user with that username or email already exists.")
        admin = User(username=normalized_username, email=normalized_email, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Administrator {admin.username} created.")

    @app.cli.command("publish-scheduled")
    def publish_scheduled():
        from app.blog.scheduling import publish_due_posts

        published_count = publish_due_posts()
        click.echo(f"Published {published_count} scheduled article(s).")

    @app.context_processor
    def inject_navigation_data():
        from flask_login import current_user

        unread_notifications = 0
        if current_user.is_authenticated:
            unread_notifications = Notification.query.filter_by(
                recipient_id=current_user.id, read_at=None
            ).count()
        return {
            "nav_categories": Category.query.order_by(Category.name).all(),
            "nav_tags": Tag.query.order_by(Tag.name).all(),
            "now_year": datetime.now().year,
            "unread_notifications": unread_notifications,
        }

    return app
