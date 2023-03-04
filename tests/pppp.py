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

    # def test_private(self):

    #     @access
    #     class Base():

    #         data: private
    #         value: private

    #         def __init__(self):
    #             self.data   = "Base_instance_data"
    #             self.value  = "Base_instance_value"

    #     class Sub1(Base):

    #         def __init__(self):
    #             self.data   = "Sub1_instance_data"
    #             self.value  = "Sub1_instance_value"

    #     with self.assertRaises(AttributeError) as cm:
    #         sub1 = Sub1()
    #     with self.assertRaises(AttributeError) as cm:
    #         print(Sub1.data)

    def test_protected(self):
        @access
        class Base():

            data: protected
            value: protected

            def __init__(self):
                self.data   = "Base_instance_data"
                self.value  = "Base_instance_value"

        class Sub1(Base):

            _value: private

            def __init__(self):
                self._value = None
                self.data   = "Sub1_instance_data"
                self.value  = "Sub1_instance_value"

            @property
            def value(self):
                return self._value
            
            @value.setter
            def value(self, value):
                self._value = value

        with self.assertRaises(AttributeError) as cm:
            sub1 = Sub1()
        # sub1.value = "Sub1_property_value"
        # self.assertEqual(sub1.data  , "Sub1_instance_data")
        # self.assertEqual(sub1.__dict__["value"] , "Sub1_instance_value")

        # self.assertEqual(sub1.value , "Sub1_property_value")
        # self.assertEqual(Sub1.data  , "Sub1_class_data")

        # self.assertEqual(type(Sub1.value) , property)


if __name__ == '__main__':
    unittest.main()
