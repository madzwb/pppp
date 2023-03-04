import inspect
from copy import deepcopy
from types import CodeType, FrameType
from typing import Annotated, Any, Type, get_type_hints, get_origin, get_args

def _is_my(frame: FrameType|None):
    return      frame.f_code.co_qualname.startswith("meta_access")     \
            or  frame.f_code.co_qualname.startswith("object_access")   \
                if frame and (frame := frame.f_back) else False

def _caller_type(frame: FrameType|None):
    cls_type = None
    cls_name = None
    while frame and (frame := frame.f_back):
        _globals = frame.f_globals
        _locals = frame.f_locals
        if not cls_name:
            qualname = frame.f_code.co_qualname
            names = qualname.split(".")
            length = len(names)
            cls_name = names[length - 2] if length > 2 else names[length - 1]
        try:
            cls_type = eval(cls_name,_globals, _locals) if cls_name else None
            break
        except Exception as e:
            pass
    return cls_type

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
        is_static = issubclass(owner_,object_access)
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



class meta_access(type):

    __constructor__ = None
    __childs__      = []
    __raccess__     = {}

    # def __init__(cls,name,base,dicts,**kwargs):
    #    super().__init__(name,base,dicts,**kwargs)

    @classmethod
    def _check_access(cls, frame: FrameType|None, name: str):
        _type = _caller_type(frame)
        __access__ = None
        try:
            __access__ = getattr(cls, "__access__")
        except Exception as e:
            pass
        _access = __access__.get(name) if __access__ else None
        if _access and not _access(_type):
            raise AttributeError(f"Access to attribute:'{name}' restricted by '{object_access.__raccess__[_access]}' keyword.")

    @classmethod
    def __is_me(cls, cls_) -> bool:
        return cls_ == meta_access

    @classmethod
    def __is_child(cls, cls_) -> bool:
        return cls_ in cls.__childs__

    @classmethod
    def __is_grandchild(cls, cls_) -> bool:
        return cls_ != None and issubclass(cls_, meta_access) and (cls_ not in cls.__childs__)
    
    def __getattribute__(cls, name: str) -> Any:
        frame = inspect.currentframe()
        if not _is_my(frame):
            cls._check_access(cls, frame, name)
        del frame

        return super(meta_access, cls).__getattribute__(name)

    def __getattr__(cls, name):
        frame = inspect.currentframe()
        if not _is_my(frame):
            cls._check_access(cls, frame, name)
        del frame

        return super(meta_access, cls).__getattribute__(name)

    def __setattr__(cls, name: str, value: Any) -> None:
        frame = inspect.currentframe()
        if not _is_my(frame):
            cls._check_access(cls, frame, name)
        del frame

        if name == "__init__" and value:
            super(meta_access, cls).__setattr__("__constructor__", value.__name__)#value.__module__ + "." + 
        
        _dict = type.__getattribute__(cls, "__dict__")
        if name in _dict:
            attribute = _dict[name]
            # # _dict = object.__getattribute__(attribute, "__dict__")
            # if "__set__" in attribute:
            if attribute and hasattr(attribute, "__set__"):
                return attribute.__set__(cls, value)
        return super(meta_access, cls).__setattr__(name, value)

    # def __repr__(cls) -> str:
    #     return super().__repr__()


class object_access(metaclass=meta_access):

    def __init_subclass__(cls, **kwargs):
        __childs__  = object.__getattribute__(object_access, "__childs__")
        __base__    = object.__getattribute__(cls   , "__base__")
        if __base__ == object_access and cls not in __childs__:
            __childs__.append(cls)
        
        access = {}
        __raccess__     = object.__getattribute__(object_access, "__raccess__")
        __annotations__ = object.__getattribute__(cls   , "__annotations__")
        for name, annotation in __annotations__.items():
            origin = get_origin(annotation)
            if origin == Annotated:
                ann_arg = get_args(annotation)
                if len(ann_arg) > 1 and ann_arg[1] in __raccess__:
                    access[name] = ann_arg[1]
        if access:
            type.__setattr__(cls, "__access__", deepcopy(access))

    def _check_access(self, frame: FrameType|None, name: str):
        _type = _caller_type(frame)
        __access__ = None
        try:
            __access__ = getattr(self, "__access__")
        except Exception as e:
            pass
        _access = __access__.get(name) if __access__ else None
        if _access and not _access(_type):
            raise AttributeError(f"Access to attribute:'{name}' restricted by '{object_access.__raccess__[_access]}' keyword.")

    def __is_instance(self, name: str):
        # __dict__ = self.__dict__
        __dict__ = object.__getattribute__(self, "__dict__")
        return __dict__ if __dict__ and name in __dict__ else None

    def __is_child_function(self, frame: FrameType|None, function: str = "__init__"):
        if      frame                               \
            and (frame := frame.f_back)             \
            and frame                               \
            and frame.f_code.co_name == function    \
            and isinstance(self, object_access):#self.__is_child(frame):
            return object.__setattr__
        return None
    
    def __is_class(self, name: str, reverse: bool = False):
        _class = None
        _attribute = None
        _set = None
        __mro__ = object.__getattribute__(type(self), "__mro__")
        if reverse:
            mro = reversed(__mro__)
        else:
            mro = __mro__
        for cls in mro:
            __dict__ = object.__getattribute__(cls, "__dict__")
            # _dict = cls.__dict__
            if name in __dict__:
                _attribute = __dict__[name]
                if _attribute:# and type(attribute) == property:
                    _set = getattr(_attribute, "__set__", None)
                    if _set:
                        # if type(_attribute) == property:
                        #     is_property = True
                        # else:
                        #     is_descriptor = True
                        break 
                _class = cls
                # cls.__class__.__setattr__(cls, name, value)
                break
        return _class, _attribute, _set

    def __getattribute__(self, name: str) -> Any:
        frame = inspect.currentframe()
        if not _is_my(frame):
            self._check_access(frame, name)
        del frame
        return super(object_access, self).__getattribute__(name)

    def __getattr__(self, name):
        frame = inspect.currentframe()
        if not _is_my(frame):
            self._check_access(frame, name)
        del frame
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:

        frame = inspect.currentframe()
        __constructor__ = type.__getattribute__(type(self),"__constructor__")
        if not __constructor__:
            __constructor__ = "__init__"
        _object = self.__is_child_function(frame,__constructor__)

        if not _object:
            if not _is_my(frame):
                self._check_access(frame, name)
            del frame
            
        _dict = self.__is_instance(name)
        _class, _attribute, _set = self.__is_class(name, _dict == None and _object != None)

        if (_dict or _object) and not _set: # Define
            self.__dict__[name] = value
            return
        if _set:                    # Descriptor
            _set(self, value)
            return
        if _class:                  # Class
            _class.__class__.__setattr__(_class, name, value)
            return

        # if _object:
        #     _object(self, name, value)
        # else:
        #     self.__dict__[name] = value
        return super(object_access, self).__setattr__(name, value)
                


def access(class_) -> Type:
    # Check if already subclass of object_access
    if issubclass(class_, object_access):
        return class_
    # Check if metaclass used
    for cls in class_.__mro__:
        meta = cls.__class__
        if  meta != type:
            # raise TypeError(f"Class: {class_} have inherit meta from {cls} by metaclass: {cls.__class__}.")
            _dict_ = meta.__dict__
            if      "__getattibute__"   in _dict_\
                or  "__getattr__"       in _dict_\
                or  "__setattr__"       in _dict_\
            :
                raise TypeError(f"Class: {class_} have inherit meta from {cls} by metaclass: {cls.__class__}, with overriden attributes' getter-setter.")
    _dict = {}
    # f = ["__dict__", "__weakref__"]
    for k,v in class_.__dict__.items():
        # if k not in f:
        try:
            _dict[k] = deepcopy(v)
        except Exception as e:
            pass
        # else:
        #     a = getattr(class_,k)
    name = class_.__name__
    del class_
    return type(name, (object_access,), _dict)

public      = Annotated[Any, None]
protected   = Annotated[Any, meta_access._meta_access__is_grandchild]
private     = Annotated[Any, meta_access._meta_access__is_child]

meta_access.__raccess__[None]                      = "public"
meta_access.__raccess__[meta_access._meta_access__is_grandchild] = "protected"
meta_access.__raccess__[meta_access._meta_access__is_child]      = "private"



if __name__ == '__main__':

    def class_name(name: str):
        return compile(name + ".__name__.lower()", "<string>", "eval")

    class Prop():

        def __init__(self, value):
            self._value = value

        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, value):
            self._value = value

    def constructor(self):
        self._value = None
        self.data   = "PropBase_instance_data"
        self.value  = "PropBase_instance_value"

    @access
    class PropBase():

        __doc__: public

        data = "PropBase_class_data"
        value = "PropBase_class_value"

    PropBase.__init__ = constructor

    class PropFirst(PropBase):

        data = "PropFirst_class_data"

        name = descriptor(class_name("PropFirst"))

        def __init__(self, value):
            super().__init__()
            self.data   = value + "_instance_data"
            self.value  = value + "_property_value"
        
        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, value):
            self._value = value

    class PropSecond(PropFirst):

        data = "PropSecond_class_data"

        name = descriptor(class_name("PropSecond"))

        def __init__(self, value):
            super().__init__(value)
            self.data   = value + "_instance_data"
            self.value  = value + "_property_value"
        
        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, value):
            self._value = value

    # subclasses = PropFirst.__childs__

    prop = Prop("Prop")
    print(prop.value)
    print(Prop.value)


    propbase = PropBase()
    print(propbase.data)
    print(propbase.value)

    prop1 = PropFirst("PropFirst")
    print(prop1.data)
    print(prop1.value)
    print(prop1.name)

    doc = getattr(PropBase,"__doc__")
    setattr(PropBase,"__doc__","PropFirst")
    doc = getattr(PropBase,"__doc__")

    print(PropBase.data)
    print(PropBase.name)

    print(PropFirst.data)
    print(PropFirst.value)
    print(PropFirst.name)
    print()
    prop2 = PropSecond("PropSecond")
    print(prop2.data)
    print(prop2.value)
    print(prop2.name)

    print(PropBase.data)
    print(PropBase.name)

    print(PropFirst.data)
    print(PropFirst.value)
    print(PropFirst.name)

    print(PropSecond.data)
    print(PropSecond.value)
    print(PropSecond.name)

    pass
