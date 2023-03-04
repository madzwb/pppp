import os
import sys
import unittest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.pppp_zwb.pppp import *



class PPPPTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    # def test_constructor(self):

    #     def constructor(self):
    #         self.data   = "Test_instance_data"
    #         self.value  = "Test_instance_value"

    #     @access
    #     class Test():

    #         data = "Test_class_data"
    #         value = "Test_class_value"

    #     Test.__init__ = constructor

    #     test = Test()
    #     self.assertEqual(test.data  , "Test_instance_data")
    #     self.assertEqual(test.value , "Test_instance_value")
    #     self.assertEqual(Test.data  , "Test_class_data")
    #     self.assertEqual(Test.value , "Test_class_value")

    # def test_property(self):

    #     @access
    #     class Base():

    #         data = "Base_class_data"
    #         value = "Base_class_value"

    #         def __init__(self):
    #             self.data   = "Base_instance_data"
    #             self.value  = "Base_instance_value"

    #     class Sub1():

    #         data = "Sub1_class_data"

    #         def __init__(self):
    #             self._value = None
    #             self.data   = "Sub1_instance_data"
    #             self.value  = "Sub1_instance_value"

    #         @property
    #         def value(self):
    #             return self._value
            
    #         @value.setter
    #         def value(self, value):
    #             self._value = value

    #     sub1 = Sub1()

    #     self.assertEqual(sub1.data  , "Sub1_instance_data")
    #     self.assertEqual(sub1.value , "Sub1_instance_value")

    #     self.assertEqual(Sub1.data  , "Sub1_class_data")

    #     self.assertEqual(type(Sub1.value) , property)


    #     class Sub2(Base):

    #         data = "Sub2_class_data"

    #         def __init__(self):
    #             self._value = None
    #             self.data   = "Sub2_instance_data"
    #             self.value  = "Sub2_instance_value"

    #         @property
    #         def value(self):
    #             return self._value
            
    #         @value.setter
    #         def value(self, value):
    #             self._value = value

    #     sub2 = Sub2()
    #     sub2.value = "Sub2_property_value"

    #     self.assertEqual(sub2.data              , "Sub2_instance_data")
    #     self.assertEqual(sub2.__dict__["value"] , "Sub2_instance_value")

    #     self.assertEqual(sub2.value , "Sub2_property_value")

    #     self.assertEqual(Sub2.data  , "Sub2_class_data")

    #     self.assertEqual(type(Sub2.value) , property)

    def test_simple(self):
        @access
        class Base():

            data_private: private
            data_protected: protected
            data_public: public

            def __init__(self):
                self.data_private   = "Base_instance_data_private"
                self.data_protected = "Base_instance_data_protected"
                self.data_public    = "Base_instance_data_public"
        
        base = Base()
        self.assertEqual(base.data_public, "Base_instance_data_public")
        with self.assertRaises(AttributeError) as cm:
            print(base.data_protected)
        with self.assertRaises(AttributeError) as cm:
            print(base.data_private)

    # def test_access_redefinition(self):
    #     @access
    #     class Base():

    #         data_private:   private
    #         data_protected: protected
    #         data_public:    public

    #         def __init__(self):
    #             self.data_private   = "Base_instance_data_private"
    #             self.data_protected = "Base_instance_data_protected"
    #             self.data_public    = "Base_instance_data_public"
        
    #     with self.assertRaises(AttributeError) as cm:
    #         class Sub1(Base):
    #             data_public: public

    # def test_subclassing(self):
    #     @access
    #     class Base():

    #         data_private:   private
    #         data_protected: protected
    #         data_public:    public

    #         def __init__(self):
    #             self.data_private   = "Base_instance_data_private"
    #             self.data_protected = "Base_instance_data_protected"
    #             self.data_public    = "Base_instance_data_public"

    #     class SubSUb1(Base):
    #         data1: private
    #         pass
    #     class SubSUb2(SubSUb1):
    #         data2: private
    #         pass
    #     class SubSUb3(SubSUb2):
    #         data3: private
    #         pass

    #     class Sub1(SubSUb3):
    #         def __init__(self):
    #             self.data_private   = "Sub_instance_data_private"
    #             self.data_protected = "Sub_instance_data_protected"
    #             self.data_public    = "Sub_instance_data_public"
                
    #     class Sub2(SubSUb3):
    #         def __init__(self):
    #             # self.data_private   = "Sub_instance_data_private"
    #             self.data_protected = "Sub_instance_data_protected"
    #             self.data_public    = "Sub_instance_data_public"

    #     with self.assertRaises(AttributeError) as cm:
    #         sub1 = Sub1()
        
    #     sub2 = Sub2()
    #     self.assertEqual(sub2.data_public, "Sub_instance_data_public")
    #     with self.assertRaises(AttributeError) as cm:
    #         print(sub2.data_protected)
    #     with self.assertRaises(AttributeError) as cm:
    #         print(sub2.data_private)

    # def test_attribute_method_replacement(self):
    #     def __getattribute__(self, name: str) -> Any:
    #         return super(Base, self).__getattribute__(name)
        
    #     def __getattr__(self, name: str) -> Any:
    #         return super(Base, self).__getattr__(name)
        
    #     def __setattr__(self, name: str, value) -> Any:
    #         return super(Base, self).__setattr__(name,value)
    #     @access
    #     class Base():

    #         data_private:   private
    #         data_protected: protected
    #         data_public:    public

    #         def __init__(self):
    #             self.data_private   = "Base_instance_data_private"
    #             self.data_protected = "Base_instance_data_protected"
    #             self.data_public    = "Base_instance_data_public"

            
    #     base = Base()
    #     self.assertEqual(base.data_public   , "Base_instance_data_public")
    #     # self.assertEqual(base.data_protected, "Base_instance_data_protected")
    #     # self.assertEqual(base.data_private  , "Base_instance_data_private")
    #     with self.assertRaises(AttributeError) as cm:
    #         print(base.data_protected)
    #     with self.assertRaises(AttributeError) as cm:
    #         print(base.data_private)
        
    #     with self.assertRaises(AttributeError) as cm:
    #         Base.__getattribute__ = __getattribute__
    #     with self.assertRaises(AttributeError) as cm:
    #         Base.__getattr__ = __getattr__
    #     with self.assertRaises(AttributeError) as cm:
    #         Base.__setattr__ = __setattr__

    # def test_attribute_method_overriding(self):
    #     @access
    #     class Base():

    #         data_private:   private
    #         data_protected: protected
    #         data_public:    public

    #         def __init__(self):
    #             self.data_private   = "Base_instance_data_private"
    #             self.data_protected = "Base_instance_data_protected"
    #             self.data_public    = "Base_instance_data_public"
            
    #         def __getattribute__(self, name: str) -> Any:
    #             return super(Base, self).__getattribute__(name)

    #     base = Base()
    #     self.assertEqual(base.data_public   , "Base_instance_data_public")
    #     with self.assertRaises(AttributeError) as cm:
    #         self.assertEqual(base.data_protected, "Base_instance_data_protected")
    #     with self.assertRaises(AttributeError) as cm:
    #         self.assertEqual(base.data_private  , "Base_instance_data_private")

    def test(self):

        class Base():
            data_public = "Base_class_data_public"
            def __init__(self):
                self.data_private = "Base_instance_data_private"

        @access
        class Sub(Base):
            data_public    : public
            data_private   : private

        sub = Sub()
        self.assertEqual(sub.data_public        , "Base_class_data_public")
        with self.assertRaises(AttributeError) as cm:
            self.assertEqual(sub.data_private   , "Base_instance_data_private")

if __name__ == '__main__':
    unittest.main()
