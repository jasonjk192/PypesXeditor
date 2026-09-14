import ctypes
import numpy as np

import pes_data

CTYPES_TO_NUMPY = {
    ctypes.c_uint8: np.uint8,
    ctypes.c_int8: np.int8,
    ctypes.c_uint16: np.uint16,
    ctypes.c_int16: np.int16,
    ctypes.c_uint32: np.uint32,
    ctypes.c_int32: np.int32,
    ctypes.c_uint64: np.uint64,
    ctypes.c_int64: np.int64,
    ctypes.c_float: np.float32,
    ctypes.c_double: np.float64,
}

PLAYER_FIELD_OVERRIDES = {
    "name": {
        "source": ("data", "name_string"),
        "dtype": "U61",
    },

    #"shirt_name": {
    #    "source": ("data", "shirt_name_string"),
    #    "dtype": "U21",
    #},
}

PLAYER_EXCLUDED_FIELDS = {
    "play_pos",
    "com_style",
    "play_skill",
    "name",
    #"shirt_name",
}

TEAM_FIELD_OVERRIDES = {
    "name": {
        "source": ("name_string",),
        "dtype": "U70",
    },
    "short_name": {
        "source": ("short_name_string",),
        "dtype": "U4",
    },
}

TEAM_EXCLUDED_FIELDS = {
    "name",
    "short_name",
}

def _ctypes_value_to_numpy(value, dtype):
    if isinstance(value, ctypes.Structure):
        result = np.zeros((), dtype=dtype)
        for field_name, _ in value._fields_:
            result[field_name] = _ctypes_value_to_numpy(getattr(value, field_name), dtype[field_name])
        return result

    if isinstance(value, ctypes.Array):
        result = np.empty(dtype.shape, dtype=dtype.base)
        for i, element in enumerate(value):
            result[i] = _ctypes_value_to_numpy(element, dtype.base)
        return result
    return value

def _ctypes_to_numpy_dtype(ctype):
    # Normal scalar type
    if ctype in CTYPES_TO_NUMPY:
        return CTYPES_TO_NUMPY[ctype]

    # ctypes array
    if issubclass(ctype, ctypes.Array):
        element_dtype = _ctypes_to_numpy_dtype(ctype._type_)
        if element_dtype is not None:
            return (element_dtype, (ctype._length_,))

    # Nested ctypes structure
    if issubclass(ctype, ctypes.Structure):
        fields = []

        for name, field_ctype in ctype._fields_:
            field_dtype = _ctypes_to_numpy_dtype(field_ctype)
            if field_dtype is not None:
                fields.append((name, field_dtype))

        if fields:
            return np.dtype(fields)

    return None

def _validate_schema(schema):
    for name, field in schema.items():
        if "source" not in field:
            raise ValueError(f"Schema field '{name}' is missing 'source'")
        if "dtype" not in field:
            raise ValueError(f"Schema field '{name}' is missing 'dtype'")

def _get_nested_attribute(obj, path):
    for name in path:
        obj = getattr(obj, name)
    return obj

def _set_nested_attribute(obj, path, value):
    for name in path[:-1]:
        obj = getattr(obj, name)
    setattr(obj, path[-1], value)

def _copy_array_to_ctypes(target, source):
    if len(target) != len(source):
        raise ValueError(f"Array size mismatch: ctypes={len(target)}, numpy={len(source)}")

    for i in range(len(target)):
        target[i] = source[i]

def _copy_structure_to_ctypes(target, source):
    for field_name, _ in target._fields_:
        target_value = getattr(target, field_name)
        source_value = source[field_name]

        if isinstance(target_value, ctypes.Array):
            _copy_array_to_ctypes(target_value, source_value)
        elif isinstance(target_value, ctypes.Structure):
            _copy_structure_to_ctypes(target_value, source_value)
        else:
            setattr(target, field_name, source_value.item()
                if isinstance(source_value, np.generic)
                else source_value,
            )

def ctypes_to_numpy(items, count, schema):
    _validate_schema(schema)

    dtype = np.dtype([
        (name, field["dtype"])
        for name, field in schema.items()
    ])

    result = np.empty(count, dtype=dtype)
    for index in range(count):
        item = items[index]

        for name, field in schema.items():
            value = _get_nested_attribute(
                item,
                field["source"]
            )

            transform = field.get("transform")
            if transform is not None:
                value = transform(value)
            value = _ctypes_value_to_numpy(value, dtype[name])
            result[index][name] = value

    return result

def numpy_to_ctypes(items, count, numpy_data, schema):
    if len(numpy_data) != count:
        raise ValueError(f"Size mismatch: ctypes={len(items)}, numpy={len(numpy_data)}")

    for index in range(count):
        item = items[index]

        for name, field in schema.items():
            value = numpy_data[name][index]
            transform = field.get("reverse_transform")
            if transform is not None:
                value = transform(value)

            target = item
            for path_name in field["source"][:-1]:
                target = getattr(target, path_name)

            final_name = field["source"][-1]
            target_value = getattr(target, final_name)
            if isinstance(target_value, ctypes.Array):
                _copy_array_to_ctypes(target_value, value)

            elif isinstance(target_value, ctypes.Structure):
                _copy_structure_to_ctypes(target_value, value)

            else:
                if isinstance(value, np.generic):
                    value = value.item()
                setattr(target, final_name, value)

def _build_player_schema():
    schema = {}
    for name, ctype in pes_data.editor_player_entry._fields_:
        if name == "data":
            continue
        if name in PLAYER_EXCLUDED_FIELDS:
            continue

        dtype = _ctypes_to_numpy_dtype(ctype)
        if dtype is not None:
            schema[name] = {
                "source": (name,),
                "dtype": dtype,
            }
    for name, ctype in pes_data.editor_player_export._fields_:
        if name in PLAYER_EXCLUDED_FIELDS:
            continue

        dtype = _ctypes_to_numpy_dtype(ctype)
        if dtype is not None:
            schema[name] = {
                "source": ("data", name),
                "dtype": dtype,
            }
            
    schema.update(PLAYER_FIELD_OVERRIDES)
    return schema

def _build_team_schema():
    schema = {}
    for name, ctype in pes_data.editor_team_entry._fields_:
        if name in TEAM_EXCLUDED_FIELDS:
            continue

        dtype = _ctypes_to_numpy_dtype(ctype)
        if dtype is not None:
            schema[name] = {
                "source": (name,),
                "dtype": dtype,
            }

    for field_name in TEAM_EXCLUDED_FIELDS:
        schema.pop(field_name, None)
    schema.update(TEAM_FIELD_OVERRIDES)
    return schema

PLAYER_SCHEMA = _build_player_schema()
TEAM_SCHEMA = _build_team_schema()