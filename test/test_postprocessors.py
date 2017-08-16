import unittest
import parse.postpocessors

class TestPostProcessors(unittest.TestCase):

    def test_cisco_iface_name_shorten(self):
        input_list = [('FastEthernet1/0/24', 'Fa1/0/24'),
                      ('TerabitEthernet0/1', 'Te0/1'),
                      ('GigabitEthernet1', 'Gi1'),
                      ('FastEthernet0/2.15', 'Fa0/2.15'),
                      ('Fast', 'Fast'),
                      ('2.18', '2.18'),
                      ('Port-channel15', 'Po15'),
                      ('E0/1', 'E0/1'),
                      ('Fa2/0/18', 'Fa2/0/18')]
        for line in input_list:
            test, result = line
            with self.subTest(line=test):
                self.assertEqual(getattr(parse.postpocessors, 'cisco_iface_name_shorten')(test), result)

    def test_cisco_route_type_expand(self):
        input_list = [('B', 'BGP'),
                      ('EX', 'EIGRP external'),
                      ('S*', 'static candidate default')]
        for line in input_list:
            test, result = line
            with self.subTest(line=test):
                self.assertEqual(getattr(parse.postpocessors, 'cisco_route_type_expand')(test), result)

    def test_to_lowercase(self):
        input_list = [('B', 'b'),
                      ('EX', 'ex'),
                      ('S*', 's*')]
        for line in input_list:
            test, result = line
            with self.subTest(line=test):
                self.assertEqual(getattr(parse.postpocessors, 'to_lowercase')(test), result)

    def test_digits_only(self):
        input_list =[("['110', None]", "110"),
                     ("abcder15fgh3tr6", "15"),
                     ("[None, '100']", '100'),
                     ("lksdfgl)", '')]
        for line in input_list:
            test, result = line
            with self.subTest(line=test):
                self.assertEqual(getattr(parse.postpocessors, 'digits_only')(test), result)