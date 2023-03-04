# pppp
Runtime attribute access like in C++, aka private, protected, public(by default).

Track constructor replacement.
Protect attribute access methods from replacement.

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

TODO:
    Metaclass inheritance tracking.
    Multiple inheritace.
