import inspect
from copy import deepcopy
from types import FrameType
from typing import Annotated, Any, Type, get_origin, get_args

"""
    Check if caller is a meta_access or object_access class
"""
def _me(frame: FrameType|None):
    return      frame.f_code.co_qualname.startswith("meta_access")     \
            or  frame.f_code.co_qualname.startswith("object_access")   \
                if frame and (frame := frame.f_back) else False


"""
    Return class name and method name from a frame
"""
def _get_caller(frame):
    cls_name = None
    fun_name = None
    if frame:
        qualname = frame.f_code.co_qualname
        names = qualname.split(".")
        length = len(names)
        cls_name = names[length - 2] if length >= 2 else names[length - 1]
        fun_name = names[-1]
    return cls_name, fun_name

"""
    Return class type of the caller. If method is overrided, returned type and method from backward frame.
"""
def _caller_type(cls: str, frame: FrameType|None):
    cls_type = None
    cls_name = None
    if frame:
        ocls_name, ofun_name = _get_caller(frame)
        if frame := frame.f_back:
            cls_name, fun_name = _get_caller(frame)
            if cls == cls_name and ofun_name == fun_name:
                frame = frame.f_back
                cls_name, fun_name = _get_caller(frame)
        
            while frame:
                _globals = frame.f_globals
                _locals = frame.f_locals
                try:
                    cls_type = eval(cls_name, _globals, _locals) if cls_name else None
                    break
                except Exception as e:
                    pass
                frame = frame.f_back

    return cls_type



class meta_access(type):

    __constructor__ = None
    __raccess__     = {}

    @staticmethod
    def __is_me(cls, cls_) -> bool:
        return cls_ == cls

    @staticmethod
    def __is_subclass(cls, cls_) -> bool:
        # inspect.isclass(cls_) - for debugger
        return cls_ and cls and (cls_ == cls or (inspect.isclass(cls_) and issubclass(cls_, cls)))

    # @staticmethod
    # def __is_child(cls, cls_) -> bool:
    #     return cls_ in cls.__subclasses__()

    # @staticmethod
    # def __is_grandchild(cls, cls_) -> bool:
    #     return cls_ != None and issubclass(cls_, meta_access) and (cls_ not in type.__subclasses__(cls))
    
    """ Just hook with access check. """
    def __getattribute__(cls, name: str) -> Any:
        frame = inspect.currentframe()
        if not _me(frame):
            cls._check_access(frame, name)
        del frame

        return super(meta_access, cls).__getattribute__(name)

    """ Just hook with access check. """
    def __getattr__(cls, name):
        frame = inspect.currentframe()
        if not _me(frame):
            cls._check_access(frame, name)
        del frame

        return super(meta_access, cls).__getattribute__(name)

    """
        Check for permissions. Process object's attributes with default behaviour.
        Store __init__ replacement with UDF in __contruction__ attribute.
    """
    def __setattr__(cls, name: str, value: Any) -> None:
        frame = inspect.currentframe()
        if not _me(frame):
            cls._check_access(frame, name)
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



public      = Annotated[Any, None]
protected   = Annotated[Any, meta_access._meta_access__is_subclass]
private     = Annotated[Any, meta_access._meta_access__is_me]

meta_access.__raccess__[None]                                   = "public"
meta_access.__raccess__[meta_access._meta_access__is_subclass]  = "protected"
meta_access.__raccess__[meta_access._meta_access__is_me]        = "private"



class object_access(metaclass=meta_access):

    # Hardcoded access to attributes method to be protected.
    # __getattribute__: protected
    # __getattr__     : protected
    # __setattr__     : protected
    __access__ = {
        "__getattribute__" : meta_access._meta_access__is_subclass,
        "__getattr__"      : meta_access._meta_access__is_subclass,
        "__setattr__"      : meta_access._meta_access__is_subclass
    }

    """
        Fill __access__ attribute with class type hints.
    """
    def __init_subclass__(cls, **kwargs):
        access = {}
        __raccess__     = type.__getattribute__(object_access   , "__raccess__")
        __annotations__ = type.__getattribute__(cls             , "__annotations__")
        for name, annotation in __annotations__.items():
            origin = get_origin(annotation)
            if origin == Annotated:
                ann_arg = get_args(annotation)
                if len(ann_arg) > 1 and ann_arg[1] in __raccess__:
                    access[name] = ann_arg[1]
        for name in access:
            _cls, _access = cls.__base__._find_access(name)
            if _cls:
                raise AttributeError(f"Access to attribute:'{name}' already defined in class:'{_cls.__name__}' with '{object_access.__raccess__[_access]}' keyword.") 
        if access:
            type.__setattr__(cls, "__access__", deepcopy(access))

    @classmethod
    def _find_access(cls, name: str, reverse: bool = False):
        _cls    = None
        _access = None
        if reverse:
            mro = reversed(cls.__mro__)
        else:
            mro = cls.__mro__
        found = False
        for _cls in mro:
            __access__ = getattr(_cls, "__access__", [])
            if name in __access__:
                _access = __access__[name]
                found = True
                break
        if not found:
            _cls = None
        return _cls, _access

    """
        Main attribute access checker.
    """
    @classmethod
    def _check_access(cls, frame: FrameType|None, name: str):
        _type   = _caller_type(cls.__name__, frame)
        _cls, _access = cls._find_access(name, True)
        if _access and _cls and not _access(_cls, _type):
            raise AttributeError(f"Access to attribute:'{name}' restricted by '{object_access.__raccess__[_access]}' keyword.")

    """
        Check if attribute is in __dict__.
    """
    def __is_instance(self, name: str):
        # __dict__ = self.__dict__
        __dict__ = object.__getattribute__(self, "__dict__")
        return __dict__ if __dict__ and name in __dict__ else None

    """
        Check if specified function is a called.
        Needed for contructor hooking.
    """
    def __is_child_function(self, frame: FrameType|None, function: str = "__init__"):
        if      frame                               \
            and (frame := frame.f_back)             \
            and frame                               \
            and frame.f_code.co_name == function    \
            and isinstance(self, object_access):#self.__is_child(frame):
            return object.__setattr__
        return None
    
    """
        Check if attribute is a property or descriptor of some class.
    """
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

    """ Just hook with access check. """
    def __getattribute__(self, name: str) -> Any:
        frame = inspect.currentframe()
        if not _me(frame):
            type(self)._check_access(frame, name)
        del frame
        return super(object_access, self).__getattribute__(name)

    """ Just hook with access check. """
    def __getattr__(self, name):
        frame = inspect.currentframe()
        if not _me(frame):
            type(self)._check_access(frame, name)
        del frame
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:

        frame = inspect.currentframe()
        if not _me(frame):
            type(self)._check_access(frame, name)
            
        __constructor__ = type.__getattribute__(type(self),"__constructor__")
        if not __constructor__:
            __constructor__ = "__init__"
        _object = self.__is_child_function(frame,__constructor__)

        del frame

        _dict = self.__is_instance(name)
        _class, _attribute, _set = self.__is_class(name, _dict == None and _object != None)

        if (_dict or _object) and not _set: # Define
            self.__dict__[name] = value
            return
        if _set:                            # Descriptor
            _set(self, value)
            return
        if _class:                          # Class
            _class.__class__.__setattr__(_class, name, value)
            return

        return super(object_access, self).__setattr__(name, value)
                


"""
    Redfine base class by type function.
    Copy all __dict__ values.
"""
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
    for k,v in class_.__dict__.items():
        try:    # to copy all copyable
            _dict[k] = deepcopy(v)
        except Exception as e:
            pass

    # TODO:
    for k,v in class_.__base__.__dict__.items():
        if not k.startswith("__") and not k.endswith("__"):
            try:    # to copy all copyable
                _dict[k] = deepcopy(v)
            except Exception as e:
                pass
    # for k,v in class_.__base__.__dict__.items():
    #     try:    # to copy all copyable
    #         _dict[k] = deepcopy(v)
    #     except Exception as e:
    #         pass
    name = class_.__name__
    del class_
    return type(name, (object_access,), _dict)

if __name__ == '__main__':

    # def class_name(name: str):
    #     return compile(name + ".__name__.lower()", "<string>", "eval")

    # class Prop():

    #     def __init__(self, value):
    #         self._value = value

    #     @property
    #     def value(self):
    #         return self._value
        
    #     @value.setter
    #     def value(self, value):
    #         self._value = value

    # def constructor(self):
    #     self._value = None
    #     self.data   = "PropBase_instance_data"
    #     self.value  = "PropBase_instance_value"

    # @access
    # class PropBase():

    #     __doc__: public

    #     data = "PropBase_class_data"
    #     value = "PropBase_class_value"

    # PropBase.__init__ = constructor

    # class PropFirst(PropBase):

    #     data = "PropFirst_class_data"

    #     name = descriptor(class_name("PropFirst"))

    #     def __init__(self, value):
    #         super().__init__()
    #         self.data   = value + "_instance_data"
    #         self.value  = value + "_property_value"
        
    #     @property
    #     def value(self):
    #         return self._value
        
    #     @value.setter
    #     def value(self, value):
    #         self._value = value

    # class PropSecond(PropFirst):

    #     data = "PropSecond_class_data"

    #     name = descriptor(class_name("PropSecond"))

    #     def __init__(self, value):
    #         super().__init__(value)
    #         self.data   = value + "_instance_data"
    #         self.value  = value + "_property_value"
        
    #     @property
    #     def value(self):
    #         return self._value
        
    #     @value.setter
    #     def value(self, value):
    #         self._value = value

    # # subclasses = PropFirst.__childs__

    # prop = Prop("Prop")
    # print(prop.value)
    # print(Prop.value)


    # propbase = PropBase()
    # print(propbase.data)
    # print(propbase.value)

    # prop1 = PropFirst("PropFirst")
    # print(prop1.data)
    # print(prop1.value)
    # print(prop1.name)

    # doc = getattr(PropBase,"__doc__")
    # setattr(PropBase,"__doc__","PropFirst")
    # doc = getattr(PropBase,"__doc__")

    # print(PropBase.data)
    # print(PropBase.name)

    # print(PropFirst.data)
    # print(PropFirst.value)
    # print(PropFirst.name)
    # print()
    # prop2 = PropSecond("PropSecond")
    # print(prop2.data)
    # print(prop2.value)
    # print(prop2.name)

    # print(PropBase.data)
    # print(PropBase.name)

    # print(PropFirst.data)
    # print(PropFirst.value)
    # print(PropFirst.name)

    # print(PropSecond.data)
    # print(PropSecond.value)
    # print(PropSecond.name)

    pass
