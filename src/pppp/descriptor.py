from typing import Any
from types import CodeType
from .pppp import object_access

class descriptor():

    def __init__(self, value: Any|None = ..., / , is_private: bool = True, is_readonly: bool = False, is_data: bool = True):
        self.value          = value
        self.is_private     = is_private
        self.is_readonly    = is_readonly
        self.is_data        = is_data
        # if self.has_data:
            # Define __set__ to make data descriptor.
            # That takes precedence over the same name entry in instance’s dictionary.
            # setattr(self.__class__,"__set__", self.__set__)
        return

    def __set_name__(self, owner_, name_) -> None:
        is_static = issubclass(owner_, object_access)
        # self.data  = self.value
        self.owner  = owner_
        self.name   = name_

    def __get__(self, object_, type_ = None) -> Any:
        if self.is_private and not object_ and type_ != self.owner:
            raise AttributeError(f"Access descriptor: {type_} != {self.owner}.")
        if self.value and isinstance(self.value, CodeType):
            try:
                self.datas = eval(self.value, globals(), locals())
                return self.datas
            except Exception as e:
                self.value = None
        return self.value
        # if type_ == self.owner:
        #     return self.value
        # if object_ is not None: # For class instance raises AttributeError, for subsequent call of __getattr__.
        #     e = AttributeError(f"Class attribute: '{self.name}' not found.",self, self.name)
        #     print(e)
        #     raise e
        # else:
        #     return None
        # return self.datas
        
    def __set__(self, object_, value_) -> None:
        if self.is_readonly: return
        # if self.read_only and not object_:
        #     e = AttributeError(f"Class attribute: '{self.name}' is read-only.",self, self.name)
        #     print(e)
        #     raise e
        # else:
        #     # _class  = object.__getattribute__(object_,  "__class__")
        #     _dict   = object.__getattribute__(object_,   "__dict__")
        #     _dict[self.name] = value
        # return
        self.value = value_
