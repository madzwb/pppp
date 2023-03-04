# pppp
Runtime attribute access like in C++, aka private, protected, public(by default).

Track constructor replacement.
Protect attribute access methods from replacement.
Basic usages:
    @access
    class Base():
        data_private    :  private      # Will be accessible only in Base class
        data_protected  :  protected    # Will be accessible only in Base class and subclasses
        data_public     :  public       # Will be accessible as usually

        def __init__(self)
            self.data_public    = "Base_instance_data_public"
            self.data_protected = "Base_instance_data_protected"
            self.data_private   = "Base_instance_data_private"

    class Sub(Base):
        def __init__(self):
            self.data_public    = "Sub_instance_data_public"
            self.data_protected = "Sub_instance_data_protected"
            self.data_private   = "Sub_instance_data_private"  --  raise ArrtibuteError

!!!CAUTIONS!!!
Modify default behavior of accessing property and descriptors.

Simple example:

    @access
    class Base():
        data: "Base_class_data"

        def __init__(self):
            self.data = "Base_instance_data"
    
    base = Base()
    
    base.data == "Base_instance_data"
    Base.data == "Base_class_data"

More examples in test/pppp.py

!!!CAUTIONS!!!
    For proper funcionality - method from base class must be invoked. 
    Ovverriding attribute access methods not fully tested.

TODO:
    Metaclass inheritance tracking.
    Multiple inheritace.
