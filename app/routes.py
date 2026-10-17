from flask import Blueprint, render_template
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