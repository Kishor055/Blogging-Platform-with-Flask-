from app.extensions import db


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    posts = db.relationship("Post", secondary="post_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
