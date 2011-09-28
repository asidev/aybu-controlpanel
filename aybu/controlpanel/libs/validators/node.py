#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from aybu.controlpanel.models import Node, Page, Section, View
from aybu.core.utils import get_object_from_python_path
from aybu.core.utils.modifiers import boolify
from aybu.core.utils.exceptions import ValidationError, ConstraintError

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
    try:
        parent = params['parent']

        if not parent is None and not isinstance(parent, Node):
            # Trying to load Node 'parent' from database.
            params['parent'] = Node.get_by_id(int(params['parent']))
    except:
        raise ValidationError('Invalid parent')

    # The type of parent is validated in the model

    if params.get('weight') is None:
        weight = Node.get_max_weight(session, params.get('parent'))
        params['weight'] = 1 if weight is None else weight

    return params


def validate_page(session, **params):

    params.update(validate_node(session, **params))

    try:
        view = params.get('view')
        if not isinstance(view, View):
            params['view'] = View.get_by_id(int(view))
    except:
        raise ValidationError('Invalid view')

    if not Page.new_page_allowed(session):
        msg = 'Max number of pages has been reached'
        log.error(msg)
        raise ConstraintError(msg)

    try:
        params['home'] = boolify(params.get('home'))
    except:
        raise ValidationError()

    return params


def validate_section(session, **params):
    params.update(validate_node(session, **params))
    return params


def validate_externallink(session, **params):
    params.update(validate_node(session, **params))
    return params


def validate_internallink(session, **params):
    params.update(validate_node(session, **params))

    try:
        linked_to = params.get('linked_to')
        if not isinstance(linked_to, Page):
            params['linked_to'] = Page.get_by_id(int(linked_to))
    except:
        raise ValidationError('Invalid Internal Link')

    return params

