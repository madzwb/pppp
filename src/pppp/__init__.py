
from .pppp import access    as access
from .pppp import public    as public
from .pppp import protected as protected
from .pppp import private   as private

# for value in list(locals().values()):
#     if getattr(value, "__module__", "").startswith(f"{__name__}."):
#         value.__module__ = __name__
