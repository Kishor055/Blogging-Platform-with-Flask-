from app.extensions import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(240), nullable=False, default="")
    posts = db.relationship("Post", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"
