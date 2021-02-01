import json
from sqlalchemy import and_, or_

def query_builder(db, model, filter):
    filter_obj = json.loads(filter)
    filter = gen(model, filter_obj)
    query = db.query(model).filter(filter)
    return query


def gen(model, filters):
    if isinstance(filters, list):
        return or_(*[gen(model, filter) for filter in filters])

    if isinstance(filters, dict):
        sub_filters = [value for key, value in filters.items() if key.isnumeric()]
        ops_2 = [gen(model, sub_filter) for sub_filter in sub_filters]

        conditions = [cdt for cdt in filters.items() if not cdt[0].isnumeric()]
        ops_1 = [get_op(model, *cdt) for cdt in conditions]
        
        return and_(*ops_1, *ops_2)


def get_op(model, key, value):
    column = key.split("__")[0]
    op = getattr(model, column) == value
    if key.endswith("__lt"):
        op = getattr(model, column) < value
    if key.endswith("__lte"):
        op = getattr(model, column) <= value
    if key.endswith("__gte"):
        op = getattr(model, column) >= value
    if key.endswith("__gt"):
        op = getattr(model, column) > value
    if key.endswith("__neq"):
        op = getattr(model, column) != value
    if key.endswith("__like"):
        op = getattr(model, column).like(value)
    if key.endswith("__ilike"):
        op = getattr(model, column).ilike(value)
    if key.endswith("__in"):
        op = getattr(model, column).in_(value)
    if key.endswith("__nin"):
        op = ~getattr(model, column).in_(value)
    if key.endswith("__is"):
        op = getattr(model, column).is_(value)
    if key.endswith("__isn"):
        op = getattr(model, column).isnot(value)
    return op