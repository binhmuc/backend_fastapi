import json
from sqlalchemy import and_, or_
from typing import Type, TypeVar
from sqlalchemy.orm import Session
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)

# A
# filter={"title__like":"%a%"}
# --->>>   SELECT * FROM items WHERE title like '%a%'

# A and B
# filter={"title__ilike":"%a%", "id__gte":1}
# --->>>   SELECT * FROM items WHERE (title ilike '%a%') AND (id >= 1)

# A and B and C
# filter={"title__like":"%a%", "id__lt":10, "owner_id": 1}
# --->>>   SELECT * FROM items WHERE (title like '%a%') AND (id < 10) AND (owner_id = 1)

# A or B
# filter=[{"title__ilike":"%a%"}, {"id__gte":1}]
# --->>>   SELECT * FROM items WHERE (title ilike '%a%') OR (id >= 1)

# A or B or C
# filter=[{"title__like":"%a%"}, {"id__lt":10}, {"owner_id": 1}]
# --->>>   SELECT * FROM items WHERE (title like '%a%') OR (id < 10) OR (owner_id = 1)

# (A and B) or C
# filter=[{"title__like":"%a%", "id__lt":10}, {"owner_id": 1}]
# --->>>   SELECT * FROM items WHERE (title like '%a%' AND id < 10) OR owner_id = 1

# (A and B and C) or D
# filter=[{"title__like":"%a%", "id__lt":10, "id__gt": 1}, {"owner_id": 1}]
# --->>>   SELECT * FROM items WHERE (title like '%a%' AND id < 10 AND id > 1) OR owner_id = 1

# (A and B) or (C and D)
# filter=[{"title__like":"%a%", "id__lt":10}, {"id__gt": 1, "owner_id": 1}]
# --->>>   SELECT * FROM items WHERE (title like '%a%' AND id < 10) OR (id > 1 AND owner_id = 1)

# (A or B) and C
# filter={"0":[{"title__like":"%a%"}, {"owner_id": 1}], "owner_id__lte": 20}
# --->>>   SELECT * FROM items WHERE (title like '%a%' OR owner_id = 1) AND owner_id <= 20

# (A or B) and (C or D)
# filter={"0":[{"title__like":"%a%"}, {"owner_id": 1}], "1":[{"owner_id__lte": 20}, {"owner_id__gte": 10}]}
# --->>>   SELECT * FROM items WHERE (title like '%a%' OR owner_id = 1) AND (owner_id <= 20 OR owner_id >= 10)


def query_builder(db: Session, model: Type[ModelType], filter: str):
    filter_obj = json.loads(filter)
    filter = gen(model, filter_obj)
    query = db.query(model).filter(filter)
    print(query)
    return query


def gen(model: Type[ModelType], filters):
    if isinstance(filters, list):
        return or_(*[gen(model, filter) for filter in filters])

    if isinstance(filters, dict):
        sub_filters = [value for key, value in filters.items() if key.isnumeric()]
        ops_2 = [gen(model, sub_filter) for sub_filter in sub_filters]

        conditions = [cdt for cdt in filters.items() if not cdt[0].isnumeric()]
        ops_1 = [get_op(model, *cdt) for cdt in conditions]
        
        return and_(*ops_1, *ops_2)


def get_op(model: Type[ModelType], key: str, value: str):
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