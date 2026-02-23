"""
CLI tool to insert news or courses into the Datapizza database.

Reads a JSON array from stdin and inserts items into the appropriate table.
Deduplicates by source_url (news) or url (courses) to avoid duplicates on
repeated runs.

Usage:
    echo '[{"title":"...","summary":"...","source":"HN",...}]' | python -m api.scrapers.insert_content --type news
    echo '[{"title":"...","description":"...","provider":"Coursera",...}]' | python -m api.scrapers.insert_content --type course
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from api.database.connection import SessionLocal, engine, Base
from api.database.models import News, Course


def parse_datetime(value: str | None) -> datetime:
    """Parse an ISO 8601 datetime string, falling back to now(UTC)."""
    if not value:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def insert_news(items: list[dict]) -> int:
    """Insert news items into the database, skipping duplicates."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted = 0
    try:
        for item in items:
            title = (item.get("title") or "").strip()
            if not title or len(title) < 10:
                continue

            source_url = item.get("source_url")
            source = item.get("source", "Unknown")

            # Dedup by source_url
            if source_url:
                existing = db.query(News).filter(News.source_url == source_url).first()
                if existing:
                    continue

            # Dedup by title + source
            existing = db.query(News).filter(
                News.title == title, News.source == source
            ).first()
            if existing:
                continue

            tags = item.get("tags", [])
            if not isinstance(tags, list):
                tags = []

            news = News(
                title=title[:255],
                summary=(item.get("summary") or title)[:2000],
                source=source[:100],
                source_url=source_url[:500] if source_url else None,
                category=item.get("category", "tech")[:50],
                tags_json=json.dumps(tags[:5]),
                author=(item.get("author") or None),
                published_at=parse_datetime(item.get("published_at")),
            )
            db.add(news)
            inserted += 1

        db.commit()
    finally:
        db.close()

    return inserted


def insert_courses(items: list[dict]) -> int:
    """Insert course items into the database, skipping duplicates."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    inserted = 0
    try:
        for item in items:
            title = (item.get("title") or "").strip()
            if not title or len(title) < 5:
                continue

            url = item.get("url", "")
            provider = item.get("provider", "Unknown")

            # Dedup by url
            if url:
                existing = db.query(Course).filter(Course.url == url).first()
                if existing:
                    continue

            # Dedup by title + provider
            existing = db.query(Course).filter(
                Course.title == title, Course.provider == provider
            ).first()
            if existing:
                continue

            tags = item.get("tags", [])
            if not isinstance(tags, list):
                tags = []

            students_count = item.get("students_count")
            if students_count is not None:
                try:
                    students_count = int(students_count)
                except (ValueError, TypeError):
                    students_count = None

            course = Course(
                title=title[:255],
                description=(item.get("description") or title)[:2000],
                provider=provider[:100],
                url=url[:500],
                instructor=item.get("instructor"),
                level=item.get("level", "beginner")[:50],
                duration=item.get("duration"),
                price=item.get("price"),
                rating=item.get("rating"),
                students_count=students_count,
                category=item.get("category", "AI")[:50],
                tags_json=json.dumps(tags[:5]),
                image_url=item.get("image_url"),
            )
            db.add(course)
            inserted += 1

        db.commit()
    finally:
        db.close()

    return inserted


def main():
    parser = argparse.ArgumentParser(
        description="Insert news or courses into the Datapizza database from JSON stdin."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["news", "course"],
        help="Type of content to insert: 'news' or 'course'",
    )
    args = parser.parse_args()

    raw = sys.stdin.read().strip()
    if not raw:
        print("Error: No JSON data provided on stdin.", file=sys.stderr)
        sys.exit(1)

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(items, list):
        items = [items]

    if args.type == "news":
        count = insert_news(items)
        print(f"Inserted {count} new news items (skipped {len(items) - count} duplicates)")
    else:
        count = insert_courses(items)
        print(f"Inserted {count} new courses (skipped {len(items) - count} duplicates)")


if __name__ == "__main__":
    main()
