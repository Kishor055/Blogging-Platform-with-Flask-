from flask import Blueprint, abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Comment, CommentReport
from app.utils.notifications import create_notification

comments_bp = Blueprint("comments", __name__, url_prefix="/comments")


@comments_bp.post("/<int:comment_id>/delete")
@login_required
def delete(comment_id: int):
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        abort(404)
    if not current_user.is_admin and comment.user_id != current_user.id:
        abort(403)
    slug = comment.post.slug
    db.session.delete(comment)
    db.session.commit()
    flash("The comment has been removed.", "info")
    return redirect(url_for("blog.detail", slug=slug) + "#comments")


@comments_bp.post("/<int:comment_id>/reply")
@login_required
def reply(comment_id: int):
    parent = db.session.get(Comment, comment_id)
    if parent is None:
        abort(404)
    if not parent.post.is_published:
        abort(404)
    depth = 0
    ancestor = parent
    while ancestor.parent is not None:
        depth += 1
        ancestor = ancestor.parent
    if depth >= 2:
        abort(400, description="Replies are limited to two nested levels.")
    content = request.form.get("content", "").strip()
    if not 2 <= len(content) <= 2000:
        flash("Replies must be between 2 and 2000 characters.", "danger")
        return redirect(url_for("blog.detail", slug=parent.post.slug) + "#comments")
    comment = Comment(
        content=content,
        author=current_user,
        post=parent.post,
        parent=parent,
    )
    db.session.add(comment)
    db.session.flush()
    recipients = {parent.user_id, parent.post.author_id}
    for recipient_id in recipients:
        create_notification(
            recipient_id,
            "reply",
            f"{current_user.username} replied to a comment on your article.",
            actor_id=current_user.id,
            post_id=parent.post_id,
            comment_id=comment.id,
        )
    db.session.commit()
    flash("Your reply has been added.", "success")
    return redirect(url_for("blog.detail", slug=parent.post.slug) + "#comment-" + str(parent.id))


@comments_bp.post("/<int:comment_id>/report")
@login_required
def report(comment_id: int):
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        abort(404)
    if not comment.post.is_published:
        abort(404)
    if comment.user_id == current_user.id:
        abort(403)
    reason = request.form.get("reason", "").strip()
    if not 5 <= len(reason) <= 500:
        flash("A report reason must be between 5 and 500 characters.", "danger")
    elif CommentReport.query.filter_by(reporter_id=current_user.id, comment_id=comment.id).first():
        flash("You have already reported this comment.", "info")
    else:
        db.session.add(CommentReport(reporter_id=current_user.id, comment=comment, reason=reason))
        db.session.commit()
        flash("Your report has been sent to the moderation team.", "success")
    return redirect(url_for("blog.detail", slug=comment.post.slug) + "#comment-" + str(comment.id))
