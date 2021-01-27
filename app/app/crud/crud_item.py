from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100, query: str
    ) -> List[Item]:
        return (
            self.query_builder(db = db, query= query)
            .filter(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def query_builder(self, db: Session,query: str) :
        if query:
            dic_args = {}
            query_objects = self.parse_query_to_object(query= query)
            for query_object in query_objects:
                if ':' == query_object['operator']:
                    dic_args[query_object['attribute']] = query_object['attribute_value']
                    continue
                if 'like' == query_object['operator']:
                    pass
                    continue
                if 'less than' == query_object['operator']:
                    pass
                    continue
                if 'grate than' == query_object['operator']:
                    pass
                    continue
            filters = self.get_filter_by_args(dic_args)
            print('-------------{}-------'.format(filters))
            db = db.query(self.model).filter(*filters)
            return db
        return db.query(self.model)


    def parse_query_to_object(self, query: str) -> []:
        query_objects = []
        for line in query.splitlines():
            command = (line[line.find('?')+1:line.find('=')])
            new_str = line[line.find(command)+len(command)+1:].replace("\"", " ").replace("{", "").replace("}", "")
            split_str = new_str.strip().split(" ")
            attribute = split_str[0]
            attribute_value = split_str[-1]
            operator = ' '.join(split_str[1:-1]).strip()
            query_objects.append({
                "command": command,
                "operator": operator,
                "attribute": attribute,
                "attribute_value": attribute_value,
            })
        return query_objects

    def get_filter_by_args(self, dic_args: dict):
        filters = []
        for key, value in dic_args.items():  # type: str, any
            if key.endswith('___min'):
                key = key[:-6]
                filters.append(getattr(self.model, key) > value)
            elif key.endswith('___max'):
                key = key[:-6]
                filters.append(getattr(self.model, key) < value)
            elif key.endswith('__min'):
                key = key[:-5]
                filters.append(getattr(self.model, key) >= value)
            elif key.endswith('__max'):
                key = key[:-5]
                filters.append(getattr(self.model, key) <= value)
            else:
                filters.append(getattr(self.model, key) == value)
        return filters


item = CRUDItem(Item)
