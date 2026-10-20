from datetime import date

from flask import Blueprint, abort, render_template, request
from .db import query

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page: every address with its turnover count and current tenant."""
    addresses = query("""
        SELECT a.id, a.street, a.unit, a.zip,
               COUNT(o.id) AS occupancy_count,
               MAX(b.name) FILTER (WHERE o.closed_on IS NULL) AS current_business
        FROM addresses a
        LEFT JOIN occupancies o ON o.address_id = a.id
        LEFT JOIN businesses  b ON b.id = o.business_id
        GROUP BY a.id
        ORDER BY occupancy_count DESC, a.street
    """)
    return render_template("index.html", addresses=addresses)


@bp.route("/search")
def search():
    """Search addresses by street or by any business that occupied them."""
    q = request.args.get("q", "").strip()
    results = []
    if q:
        # Two halves joined with UNION instead of one OR across the join,
        # so each half can use its trigram index (see docs/performance.md)
        results = query("""
            SELECT a.id, a.street, a.unit, a.zip
            FROM addresses a
            WHERE a.street ILIKE %(pattern)s
            UNION
            SELECT a.id, a.street, a.unit, a.zip
            FROM addresses a
            JOIN occupancies o ON o.address_id = a.id
            JOIN businesses  b ON b.id = o.business_id
            WHERE b.name ILIKE %(pattern)s
            ORDER BY street, unit
            LIMIT 50
        """, {"pattern": f"%{q}%"})
    return render_template("search.html", q=q, results=results)


@bp.route("/leaderboard")
def leaderboard():
    """Most cursed storefronts: highest curse score first (see 004_curse_view.sql)."""
    rows = query("""
        SELECT id, street, unit, zip, occupancy_count, curse_score,
               closures_last_10y AS recent_closures,
               ROUND(avg_lifespan_days / 30.0, 1) AS avg_lifespan_months
        FROM curse_scores
        WHERE occupancy_count >= 2
        ORDER BY curse_score DESC, occupancy_count DESC, avg_lifespan_months ASC NULLS LAST
        LIMIT 25
    """)
    return render_template("leaderboard.html", rows=rows)

@bp.route("/address/<int:address_id>")
def address_detail(address_id):
    """Address page: one storefront and every business that has occupied it."""
    rows = query("SELECT id, street, unit, city, zip FROM addresses WHERE id = %s",
                 (address_id,))
    if not rows:
        abort(404)
    address = rows[0]

    # Oldest first, so the page reads like a timeline
    occupancies = query("""
        SELECT b.name, c.name AS category, o.opened_on, o.closed_on
        FROM occupancies o
        JOIN businesses b ON b.id = o.business_id
        LEFT JOIN categories c ON c.id = b.category_id
        WHERE o.address_id = %s
        ORDER BY o.opened_on
    """, (address_id,))

    # Chart data for the timeline (issue #7). Dates become ISO strings so
    # Jinja's tojson filter can pass them to JavaScript. Businesses that are
    # still open get today's date as their end, so their bar runs to today.
    today = date.today()
    timeline = [
        {
            "name": o["name"],
            "start": o["opened_on"].isoformat(),
            "end": (o["closed_on"] or today).isoformat(),
            "open": o["closed_on"] is None,
        }
        for o in occupancies
    ]

    return render_template("address.html", address=address,
                           occupancies=occupancies, timeline=timeline)
