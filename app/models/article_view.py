from datetime import date

from app.extensions import db


class ArticleView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viewed_on = db.Column(db.Date, nullable=False, default=date.today, index=True)
    visitor_key = db.Column(db.String(64), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True)
    post = db.relationship("Post", back_populates="views")
    __table_args__ = (
        db.UniqueConstraint("post_id", "viewed_on", "visitor_key", name="uq_article_view_daily_visitor"),
    )
