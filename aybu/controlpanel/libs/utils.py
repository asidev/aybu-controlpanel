
import aybu.controlpanel.models as models

def load_entity_from_string(entity):
    """ Load an entity class from the models using its string name.

        Return the argument unchanged when it is not a string.
    """

    if not isinstance(type_, basestring):
        return entity

    if hasattr(models, type_):
        return getattr(models, type_)

    raise ValueError('No entity named %s in the model.' % entity)
