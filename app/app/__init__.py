import functools
import itertools
from typing import Any

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN


Allow = "Allow" 
Deny = "Deny" 

Everyone = "system:everyone"  
Authenticated = "system:authenticated"  


class _AllPermissions:

    def __contains__(self, other):
        
        return True

    def __str__(self):
        
        return "permissions:*"


All = _AllPermissions()


DENY_ALL = (Deny, Everyone, All)  
ALOW_ALL = (Allow, Everyone, All) 

permission_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN,
    detail="Insufficient permissions",
    headers={"WWW-Authenticate": "Bearer"},
)


def configure_permissions(
    active_principals_func: Any,
    permission_exception: HTTPException = permission_exception,
):
    
    active_principals_func = Depends(active_principals_func)

    return functools.partial(
        permission_dependency_factory,
        active_principals_func=active_principals_func,
        permission_exception=permission_exception,
    )


def permission_dependency_factory(
    permission: str,
    resource: Any,
    active_principals_func: Any,
    permission_exception: HTTPException,
):
   
    if callable(resource):
        dependable_resource = Depends(resource)
    else:
        dependable_resource = Depends(lambda: resource)

        resource=dependable_resource, principals=active_principals_func
    ):
        if has_permission(principals, permission, resource):
            return resource
        raise permission_exception

    return Depends(permission_dependency)


def has_permission(
    user_principals: list, requested_permission: str, resource: Any
):
    acl = normalize_acl(resource)

    for action, principal, permissions in acl:
        if isinstance(permissions, str):
            permissions = {permissions}
        if requested_permission in permissions:
            if principal in user_principals:
                return action == Allow
    return False


def list_permissions(user_principals: list, resource: Any):
    
    acl = normalize_acl(resource)

    acl_permissions = (permissions for _, _, permissions in acl)
    as_iterables = ({p} if not is_like_list(p) else p for p in acl_permissions)
    permissions = set(itertools.chain.from_iterable(as_iterables))

    return {
        str(p): has_permission(user_principals, p, acl) for p in permissions
    }



def normalize_acl(resource: Any):
    
    acl = getattr(resource, "__acl__", None)
    if callable(acl):
        return acl()
    elif acl is not None:
        return acl
    elif is_like_list(resource):
        return resource
    return []


def is_like_list(something):
    if isinstance(something, str):
        return False
    return hasattr(something, "__iter__")
