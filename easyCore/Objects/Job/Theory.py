#  SPDX-FileCopyrightText: 2023 easyCore contributors  <core@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021-2023 Contributors to the easyCore project <https://github.com/easyScience/easyCore

from typing import Any
from typing import List

from easyCore.Objects.ObjectClasses import BaseObj
from easyCore.Objects.ObjectClasses import Parameter


class TheoryBase(BaseObj):
    """
    This virtual class allows for the creation of technique-specific Theory objects.
    """
    def __init__(self, name: str, parameters: List[Parameter], *args, **kwargs):
        super(TheoryBase, self).__init__(name, *args, **kwargs)
        self.parameters = parameters


    # required dunder methods
    def __str__(self):
        return f"Theory: {self.name}"
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)
    
    def __copy__(self) -> 'TheoryBase':
        raise NotImplementedError("Copy not implemented")
        #return super().__copy__()
    
    def __deepcopy__(self, memo: Any) -> 'TheoryBase':
        raise NotImplementedError("Deepcopy not implemented")
        #return super().__deepcopy__(memo)
    
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError("Equality not implemented")
        #return super().__eq__(other)
    