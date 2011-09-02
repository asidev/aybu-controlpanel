
import aybu.controlpanel.models as models
import aybu.controlpanel.validators as validators

def load_entity_from_string(entity):
    """ Load an entity class from the models using its string name."""

    if not isinstance(entity, basestring):
        entity = str(entity)

    if hasattr(models, entity):
        return getattr(models, entity)

    raise ValueError('No entity named %s exists in the model.' % entity)

def load_validator_from_string(validator):
    """ Load a validator callable from 'validators' package using its name."""

    if not isinstance(validator, basestring):
        validator = str(validator)

    if hasattr(models, validator):
        return getattr(models, validator)

    raise ValueError('No validator named %s exists.' % validator)
