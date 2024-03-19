import os
import sys
from collections import OrderedDict

from vdfutils import parse_vdf, format_vdf, VDFConsistencyError

PARSE_VDF_DIR = 'parse_vdf'
PARSE_VDF_TEST_CASES = (
    (
        'test1.vdf',                # File    
        False,                      # Repeat
        True,                       # Escape
        {                           # Expected
            'key1'  :   'value1',
            'key2'  :   'value2',
            'key3'  :   'value3',
            'key4'  :   'value4',
            'key5'  :   'value5',
        },
    ),
    (
        'test2.vdf',
        False,
        True,
        {
            'key1'  :   'value1',
            'key2'  :   'value2',
            'key3'  :   'value3',
            'key4'  :   'value4',
            'key5'  :   'value5',
        },
    ),
    (
        'test3.vdf',
        False,
        True,
        {
            'key1'  :   'value1',
            'key2'  :   'value2',
            'key3'  :   'value3',
            'key4'  :   'value4',
            'key5'  :   'value5',
        },
    ),
    (
        'test4.vdf',
        False,
        True,
        {
            'body'  :   {
                'head'  :   'skull',
                'torso' :   {
                    'upper' :   {
                        'arm1'  :   'left',
                        'arm2'  :   'right',
                    },
                    'lower' :   {
                        'leg1'  :   'left',
                        'leg2'  :   'right',
                    },
                },
            },
        },
    ),
    (
        'test5.vdf',
        False,
        True,
        VDFConsistencyError("Brackets without heading!"),
    ),
    (
        'test6.vdf',
        False,
        True,
        VDFConsistencyError("Brackets without heading!"),
    ),
    (
        'test7.vdf',
        False,
        True,
        VDFConsistencyError("Mismatched brackets!"),
    ),
    (
        'test8.vdf',
        False,
        True,
        {
            'This'  :   'is',
            'some'  :   'perfectly',
            'valid' :   'data.',
        },
    ),
    (
        'test9.vdf',
        False,
        True,
        VDFConsistencyError("Key 'valid.' without value!"),
    ),
    (
        'test10.vdf',
        False,
        True,
        {
            'foo'   :   'repeat',
        },
    ),
    (
        'test10.vdf',
        True,
        True,
        {
            'foo'   :   ['these', 'keys', 'repeat'],
        },
    ),
    (
        'test11.vdf',
        False,
        True,
        {},
    ),
    (
        'test12.vdf',
        False,
        True,
        {
            'visible'   :   'value',
            'can'       :   {
                'see'   :   'everything',
                'in'    :   'here',
            },
        },
    ),
    (
        'test13.vdf',
        False,
        True,
        {
            'this'  :   {
                'is'    :   {
                    'a' :   {
                        'set'   :   {
                            'of'    :   {
                                'ultra' :   {
                                    'nested'    :   {
                                        'brackets'  :   {}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    ),
    (
        'test14.vdf',
        False,
        True,
        VDFConsistencyError('Mismatched brackets!'),
    ),
    (
        'test15.vdf',
        False,
        True,
        VDFConsistencyError('Mismatched brackets!'),
    ),
    (
        'test16.vdf',
        False,
        True,
        {
            'escaped'   :   {
                'tab'           :   '\t',
                'newline'       :   '\n',
                'quote'         :   '\"',
                'backslash'     :   '\\',
                'everything'    :   '\t\n\"\\\\\"\n\t',
            }
        },
    ),
    (
        'test16.vdf',
        False,
        False,
        VDFConsistencyError('Mismatched quotes!'),
    ),
    (
        'test17.vdf',
        False,
        False,
        {
            'unescaped'   :   {
                'tab'           :   '\\t',
                'newline'       :   '\\n',
                'backslash'     :   '\\\\',
                'everything'    :   '\\t\\n\\',
                '\\\\\\\\\\'    :   '\\n\\t',
            }
        },
    ),
    (
        'test18.vdf',
        True,
        False,
        {
            'foo'   :   ['these', 'keys', 'repeat'],
            'bar'   :   [
                {'this' :   'repeats'},
                {
                    'this'  :   'repeats',
                    'yet'   :   'again',
                },
                {'and'  :   'again'},
            ],
            'spam'  :   [
                {
                    'id'        :   '0',
                    'nested'    :   [
                        {
                            'id'    :   '0',
                            'repeating' :   'keys',
                        },
                        {
                            'id'    :   '1',
                            'repeating' :   'keys',
                        },
                        {
                            'id'    :   '2',
                            'repeating' :   'keys',
                        },
                    ],
                },
                {
                    'id'        :   '1',
                    'nested'    :   [
                        {
                            'id'    :   '0',
                            'repeating' :   'keys',
                        },
                        {
                            'id'    :   '1',
                            'repeating' :   'keys',
                        },
                        {
                            'id'    :   '2',
                            'repeating' :   'keys',
                        },
                    ],
                },
            ],
        },
    ),
)

FORMAT_VDF_DIR = 'format_vdf'
FORMAT_VDF_TEST_CASES = (
    (
        OrderedDict(
                (
                    ('key1', 'value1'),
                    ('key2', 'value2'),
                    ('key3', 'value3'),
                    ('key4', 'value4'),
                    ('key5', 'value5'),
                ),
            ),                      # Data
        False,                      # Escape
        'test1.vdf',                # Expected (file)
    ),
    (
        {
            'body' : OrderedDict((
                ('head', 'skull'),
                ('torso',
                    OrderedDict((
                        ('upper',
                            OrderedDict((
                                ('arm1', 'left'),
                                ('arm2', 'right')))),
                        ('lower',
                            OrderedDict((
                                ('leg1', 'left'),
                                ('leg2', 'right'))))))))),
        },
        False,
        'test2.vdf',
    ),
    (
        {'foo' : ['these', 'keys', 'repeat']},
        False,
        'test3.vdf',
    ),
    (
        OrderedDict(
                (
                    ('here', 123),
                    ('are', 456),
                    ('some', 789),
                    ('numbers', 0),
                ),
            ),
        False,
        'test4.vdf',
    ),
)


def test_parse_vdf():
    for file, repeat, escape, expected in PARSE_VDF_TEST_CASES:
        with open(os.path.join(PARSE_VDF_DIR, file), 'r') as f:
            data = f.read()
            
        print("Testing {}...".format(file))
        print("Expected:\n", expected)
        
        if isinstance(expected, Exception):
            result = None
            try:
                result = parse_vdf(data, allowRepeats=repeat, escape=escape)
                
            except expected.__class__ as e:
                print("Result:\n", e)
                
                assert str(e) == str(expected)
                
                print("Passed!\n")
                continue
                
            print("Result:\n", result)
            assert result is None
            
        else:
            result = parse_vdf(data, allowRepeats=repeat, escape=escape)
            
            print("Result:\n", result)
            
            assert result == expected
            
            print("Passed!\n")
            
    print("All parse_vdf() tests passed!")
    return 0
    
    
def test_format_vdf():
    for i, (data, escape, file) in enumerate(FORMAT_VDF_TEST_CASES):
        print("Test {}...".format(i))
        
        with open(os.path.join(FORMAT_VDF_DIR, file), 'r') as f:
            expected = f.read()
            
        print("Expected:\n", expected)
        
        result = format_vdf(data, escape=escape)
        
        print("Result:\n", result)
        
        assert result.strip() == expected.strip()
        
        print("Passed!\n")
        
    print("All format_vdf() tests passed!")
    return 0
    
    
if __name__ == '__main__':
    assert test_parse_vdf() == 0
    print("")
    
    assert test_format_vdf() == 0
    print("All tests passed!")
    
    