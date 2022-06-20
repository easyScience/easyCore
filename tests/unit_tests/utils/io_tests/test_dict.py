__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from copy import deepcopy
from typing import Type

import pytest
from .test_core import dp_param_dict, skip_dict, check_dict, A, Descriptor, Parameter
from easyCore.Utils.io.dict import DictSerializer, DataDictSerializer


def recursive_remove(d, remove_keys: list) -> dict:
    """
    Remove keys from a dictionary.
    """
    if not isinstance(remove_keys, list):
        remove_keys = [remove_keys]
    if isinstance(d, dict):
        dd = {}
        for k in d.keys():
            if k not in remove_keys:
                dd[k] = recursive_remove(d[k], remove_keys)
        return dd
    else:
        return d


########################################################################################################################
# TESTING ENCODING
########################################################################################################################
@pytest.mark.parametrize(**skip_dict)
@pytest.mark.parametrize(**dp_param_dict)
def test_variable_DictSerializer(dp_kwargs: dict, dp_cls: Type[Descriptor], skip):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    obj = dp_cls(**data_dict)

    dp_kwargs = deepcopy(dp_kwargs)

    if isinstance(skip, str):
        del dp_kwargs[skip]

    if not isinstance(skip, list):
        skip = [skip]

    enc = obj.encode(skip=skip, encoder=DictSerializer)

    expected_keys = set(dp_kwargs.keys())
    obtained_keys = set(enc.keys())

    dif = expected_keys.difference(obtained_keys)

    assert len(dif) == 0

    check_dict(dp_kwargs, enc)


@pytest.mark.parametrize(**skip_dict)
@pytest.mark.parametrize(**dp_param_dict)
def test_variable_DataDictSerializer(dp_kwargs: dict, dp_cls: Type[Descriptor], skip):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    obj = dp_cls(**data_dict)

    if isinstance(skip, str):
        del data_dict[skip]

    if not isinstance(skip, list):
        skip = [skip]

    enc_d = obj.encode(skip=skip, encoder=DataDictSerializer)

    expected_keys = set(data_dict.keys())
    obtained_keys = set(enc_d.keys())

    dif = expected_keys.difference(obtained_keys)

    assert len(dif) == 0

    check_dict(data_dict, enc_d)


@pytest.mark.parametrize(
    "encoder", [None, DataDictSerializer], ids=["Default", "DataDictSerializer"]
)
@pytest.mark.parametrize(**skip_dict)
@pytest.mark.parametrize(**dp_param_dict)
def test_variable_encode_data(dp_kwargs: dict, dp_cls: Type[Descriptor], skip, encoder):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    obj = dp_cls(**data_dict)

    if isinstance(skip, str):
        del data_dict[skip]

    if not isinstance(skip, list):
        skip = [skip]

    enc_d = obj.encode_data(skip=skip, encoder=encoder)

    expected_keys = set(data_dict.keys())
    obtained_keys = set(enc_d.keys())

    dif = expected_keys.difference(obtained_keys)

    assert len(dif) == 0

    check_dict(data_dict, enc_d)


@pytest.mark.parametrize(**skip_dict)
@pytest.mark.parametrize(**dp_param_dict)
def test_custom_class_DictSerializer_encode(
    dp_kwargs: dict, dp_cls: Type[Descriptor], skip
):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    a_kw = {data_dict["name"]: dp_cls(**data_dict)}

    full_d = {
        "@module": A.__module__,
        "@class": A.__name__,
        "@version": None,
        "name": "A",
        dp_kwargs["name"]: deepcopy(dp_kwargs),
    }

    if not isinstance(skip, list):
        skip = [skip]

    full_d = recursive_remove(full_d, skip)

    obj = A(**a_kw)

    enc = obj.encode(skip=skip, encoder=DictSerializer)
    expected_keys = set(full_d.keys())
    obtained_keys = set(enc.keys())

    dif = expected_keys.difference(obtained_keys)

    assert len(dif) == 0

    check_dict(full_d, enc)


@pytest.mark.parametrize(**skip_dict)
@pytest.mark.parametrize(**dp_param_dict)
def test_custom_class_DataDictSerializer(
    dp_kwargs: dict, dp_cls: Type[Descriptor], skip
):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    a_kw = {data_dict["name"]: dp_cls(**data_dict)}

    full_d = {"name": "A", dp_kwargs["name"]: data_dict}

    full_d = recursive_remove(full_d, skip)

    obj = A(**a_kw)

    enc = obj.encode(skip=skip, encoder=DataDictSerializer)
    expected_keys = set(full_d.keys())
    obtained_keys = set(enc.keys())

    dif = expected_keys.difference(obtained_keys)

    assert len(dif) == 0

    check_dict(full_d, enc)


@pytest.mark.parametrize(
    "encoder", [None, DataDictSerializer], ids=["Default", "DataDictSerializer"]
)
@pytest.mark.parametrize(**dp_param_dict)
def test_custom_class_encode_data(dp_kwargs: dict, dp_cls: Type[Descriptor], encoder):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    a_kw = {data_dict["name"]: dp_cls(**data_dict)}

    full_d = {"name": "A", dp_kwargs["name"]: data_dict}

    obj = A(**a_kw)

    enc = obj.encode_data(encoder=encoder)
    expected_keys = set(full_d.keys())
    obtained_keys = set(enc.keys())

    dif = expected_keys.difference(obtained_keys)

    assert len(dif) == 0

    check_dict(full_d, enc)


########################################################################################################################
# TESTING DECODING
########################################################################################################################
@pytest.mark.parametrize(**dp_param_dict)
def test_variable_DictSerializer_decode(dp_kwargs: dict, dp_cls: Type[Descriptor]):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    obj = dp_cls(**data_dict)
    if "units" in data_dict.keys():
        data_dict["unit"] = data_dict.pop("units")
    if "value" in data_dict.keys():
        data_dict["raw_value"] = data_dict.pop("value")

    enc = obj.encode(encoder=DictSerializer)
    dec = obj.decode(enc, decoder=DictSerializer)

    for k in data_dict.keys():
        if hasattr(obj, k) and hasattr(dec, k):
            assert getattr(obj, k) == getattr(dec, k)
        else:
            raise AttributeError(f"{k} not found in decoded object")


@pytest.mark.parametrize(**dp_param_dict)
def test_variable_DataDictSerializer_decode(dp_kwargs: dict, dp_cls: Type[Descriptor]):
    data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != "@"}

    obj = dp_cls(**data_dict)
    if "units" in data_dict.keys():
        data_dict["unit"] = data_dict.pop("units")
    if "value" in data_dict.keys():
        data_dict["raw_value"] = data_dict.pop("value")

    enc = obj.encode(encoder=DataDictSerializer)
    with pytest.raises(NotImplementedError):
        dec = obj.decode(enc, decoder=DataDictSerializer)


#
# @pytest.mark.parametrize(**dp_param_dict)
# def test_custom_class_DictSerializer_decode(dp_kwargs: dict, dp_cls: Type[Descriptor]):
#
#     data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != '@'}
#
#     a_kw = {
#         data_dict['name']: dp_cls(**data_dict)
#     }
#
#     obj = A(**a_kw)
#
#     enc = obj.encode(encoder=DictSerializer)
#
#     stripped_encode = {k: v for k, v in enc.items() if k[0] != '@'}
#     stripped_encode[data_dict['name']] = data_dict
#
#     dec = obj.decode(enc, decoder=DictSerializer)
#
#     def test_objs(reference_obj, test_obj, in_dict):
#         if 'value' in in_dict.keys():
#             in_dict['raw_value'] = in_dict.pop('value')
#         if 'units' in in_dict.keys():
#             del in_dict['units']
#         for k in in_dict.keys():
#             if hasattr(reference_obj, k) and hasattr(test_obj, k):
#                 if isinstance(in_dict[k], dict):
#                     test_objs(getattr(obj, k), getattr(test_obj, k), in_dict[k])
#                 assert getattr(obj, k) == getattr(dec, k)
#             else:
#                 raise AttributeError(f"{k} not found in decoded object")
#     test_objs(obj, dec, stripped_encode)
#
#
# @pytest.mark.parametrize(**skip_dict)
# @pytest.mark.parametrize(**dp_param_dict)
# def test_custom_class_DataDictSerializer(dp_kwargs: dict, dp_cls: Type[Descriptor], skip):
#     data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != '@'}
#
#     a_kw = {
#         data_dict['name']: dp_cls(**data_dict)
#     }
#
#     full_d = {
#         "name":        "A",
#         dp_kwargs['name']: data_dict
#     }
#
#     full_d = recursive_remove(full_d, skip)
#
#     obj = A(**a_kw)
#
#     enc = obj.encode(skip=skip, encoder=DataDictSerializer)
#     expected_keys = set(full_d.keys())
#     obtained_keys = set(enc.keys())
#
#     dif = expected_keys.difference(obtained_keys)
#
#     assert len(dif) == 0
#
#     check_dict(full_d, enc)
#
#
# @pytest.mark.parametrize('encoder', [None, DataDictSerializer], ids=['Default', 'DataDictSerializer'])
# @pytest.mark.parametrize(**dp_param_dict)
# def test_custom_class_encode_data(dp_kwargs: dict, dp_cls: Type[Descriptor], encoder):
#     data_dict = {k: v for k, v in dp_kwargs.items() if k[0] != '@'}
#
#     a_kw = {
#         data_dict['name']: dp_cls(**data_dict)
#     }
#
#     full_d = {
#         "name":        "A",
#         dp_kwargs['name']: data_dict
#     }
#
#     obj = A(**a_kw)
#
#     enc = obj.encode_data(encoder=encoder)
#     expected_keys = set(full_d.keys())
#     obtained_keys = set(enc.keys())
#
#     dif = expected_keys.difference(obtained_keys)
#
#     assert len(dif) == 0
#
#     check_dict(full_d, enc)