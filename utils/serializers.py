from typing import List, Tuple
from django.db.models import Model
from django.core.serializers import serialize
import json


def serialize_model(model: Model, keys_to_remove: List[str]) -> dict:
    """Serialize a model

    Args:
        model (Model): Django model to serialize
        keys_to_remove (List[str]): Values to ignore

    Returns:
        dict: Serialized model
    """
    serialized_data = serialize("json", [model])
    data = json.loads(serialized_data)[0]["fields"]
    for key in keys_to_remove:
        data.pop(key, None)
    return data
