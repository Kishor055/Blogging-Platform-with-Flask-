"""Seed starter categories and tags.

Revision ID: b31d7e2a9c41
Revises: 7af4a4ef9db8
Create Date: 2026-11-01
"""
from alembic import op
import sqlalchemy as sa


revision = "b31d7e2a9c41"
down_revision = "7af4a4ef9db8"
branch_labels = None
depends_on = None


CATEGORIES = [
    ("Technology", "technology", "Software, tools, and the digital world."),
    ("Lifestyle", "lifestyle", "Ideas for everyday life and personal growth."),
    ("Travel", "travel", "Places, journeys, and travel notes."),
    ("Food", "food", "Recipes, food culture, and good meals."),
    ("Health & Wellness", "health-wellness", "Wellbeing, health, and mindful living."),
    ("Business", "business", "Entrepreneurship, work, and business."),
    ("Education", "education", "Learning, teaching, and useful explainers."),
    ("Culture", "culture", "Books, arts, media, and society."),
]

TAGS = [
    ("Python", "python"),
    ("Flask", "flask"),
    ("Web Development", "web-development"),
    ("Artificial Intelligence", "artificial-intelligence"),
    ("Productivity", "productivity"),
    ("Tutorial", "tutorial"),
    ("Design", "design"),
    ("Startups", "startups"),
    ("Personal Growth", "personal-growth"),
    ("Remote Work", "remote-work"),
    ("Reviews", "reviews"),
    ("Opinion", "opinion"),
]


def _insert_missing(table_name, rows):
    columns = [sa.column("name", sa.String()), sa.column("slug", sa.String())]
    if table_name == "category":
        columns.append(sa.column("description", sa.String()))
    table = sa.table(table_name, *columns)
    bind = op.get_bind()
    existing = bind.execute(sa.select(table.c.name, table.c.slug)).all()
    names = {name.casefold() for name, _slug in existing}
    slugs = {slug for _name, slug in existing}
    for row in rows:
        name, slug = row[:2]
        if name.casefold() in names or slug in slugs:
            continue
        values = {"name": name, "slug": slug}
        if table_name == "category":
            values["description"] = row[2]
        bind.execute(sa.insert(table).values(**values))
        names.add(name.casefold())
        slugs.add(slug)


def upgrade():
    _insert_missing("category", CATEGORIES)
    _insert_missing("tag", TAGS)


def downgrade():
    bind = op.get_bind()
    for name, slug, _description in CATEGORIES:
        bind.execute(
            sa.text("DELETE FROM category WHERE name = :name AND slug = :slug"),
            {"name": name, "slug": slug},
        )
    for name, slug in TAGS:
        bind.execute(
            sa.text("DELETE FROM tag WHERE name = :name AND slug = :slug"),
            {"name": name, "slug": slug},
        )
