from datetime import date

from flask import Blueprint, abort, render_template
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
        SELECT b.name, b.category, o.opened_on, o.closed_on
        FROM occupancies o
        JOIN businesses b ON b.id = o.business_id
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
