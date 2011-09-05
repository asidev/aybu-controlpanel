#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aybu.controlpanel.models import Menu
from aybu.controlpanel.models import Node
from aybu.controlpanel.models import Page
from aybu.controlpanel.models import Section
from aybu.controlpanel.libs.utils import get_object_from_python_path
from aybu.controlpanel.libs.exceptions import ValidationError
import logging

__all__ = []

log = logging.getLogger(__name__)


def validate_create(session, cls, **params):
    """Validate 'cls' and 'params' following rules of application logic.

    """
    if cls == Node:
        raise ValidationError('cls: Node creation is not allowed!')

    try:
        validate_lineage(cls, Node)

    except ValueError as e:
        raise ValidationError('cls: ', *e.args)

    validator = 'aybu.controlpanel.libs.validators.node.validate_%s'
    validator = get_object_from_python_path(validator % cls.__name__.lower())
    return validator(session, **params)


def validate_lineage(cls, ancestor):
    """Check if 'cls' is a subclass of 'ancestor'.

    """
    if not issubclass(cls, ancestor):
        msg = '%s is not a subclass of %s.' % (cls.__name__, ancestor.__name__)
        raise ValueError(msg)


def validate_node(session, **params):
    """Validate input values that can be used to create a Node instance.

    """
    #FIXME: Is 'parent' mandatory?
    if 'parent' in params:
        if not isinstance(params['parent'], Node):
            # Load Node 'parent' from database.
            params['parent'] = Node.get_by_id(params['parent'])

        #FIXME: This check is needed because the model is wrong!
        if not isinstance(params['parent'], (Menu, Section, Page)):
            msg = 'parent: %s cannot have children.' % params['parent'].__name__
            raise ValidationError(msg)

    if params.get('weight') is None:
        weight = Node.get_max_weight(session, params.get('parent'))
        params['weight'] = 1 if weight is None else weight

    return params


def validate_page(session, **params):

    params.update(validate_node(session, **params))
    """
    if not isinstance(params.get('view'), View):
        msg = 'view: %s is not a View instance.' % params.get('view')
        raise ValidationError(msg)

    if not new_page_allowed(session):
        log.error('Max number of pages has been reached')
        raise QuotaException(error)
    """

    return params
