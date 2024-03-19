import vdfutils
from vdfutils import _Field, _OpenBrace, _CloseBrace, VDFConsistencyFailure

_tokenize_vdf = vdfutils._tokenize_vdf

# General
assert list(_tokenize_vdf('')) == []
assert list(_tokenize_vdf('   ')) == []
assert list(_tokenize_vdf('abc')) == [_Field('abc')]
assert list(_tokenize_vdf('abc def')) == [_Field('abc'), _Field('def')]
assert list(_tokenize_vdf('abc def     ghi')) == [
    _Field('abc'), _Field('def'), _Field('ghi')
]
assert list(_tokenize_vdf('abc def  {}   ghi')) == [
    _Field('abc'), _Field('def'), _OpenBrace(), _CloseBrace(), _Field('ghi')
]
assert list(_tokenize_vdf('abc def  {}   {ghi}')) == [
    _Field('abc'), _Field('def'), _OpenBrace(), _CloseBrace(), _OpenBrace(),
    _Field('ghi'), _CloseBrace()
]
assert list(_tokenize_vdf('abc def  {}   {"ghi"}')) == [
    _Field('abc'), _Field('def'), _OpenBrace(), _CloseBrace(), _OpenBrace(),
    _Field('ghi'), _CloseBrace()
]
assert list(_tokenize_vdf('"abc def  {}   {ghi}"')) == [
    _Field('abc def  {}   {ghi}')
]
assert list(_tokenize_vdf('"abc def  {}   ""{ghi}"')) == [
    _Field('abc def  {}   '), _Field('{ghi}')
]
assert list(_tokenize_vdf('"abc"def  {}   ""{ghi}')) == [
    _Field('abc'), _Field('def'), _OpenBrace(), _CloseBrace(), _Field(''),
    _OpenBrace(), _Field('ghi'), _CloseBrace()
]
assert list(_tokenize_vdf('"abc"def"ghi"jkl"mno"')) == [
    _Field('abc'), _Field('def'), _Field('ghi'), _Field('jkl'), _Field('mno')
]
assert list(_tokenize_vdf('"\\abc\\""def"ghi"jkl"m\\no"')) == [
    _Field('\\abc"'), _Field('def'), _Field('ghi'),
    _Field('jkl'), _Field('m\no')
]
assert list(_tokenize_vdf('""""""')) == [
    _Field(''), _Field(''), _Field('')
]

# Escape chars
assert list(_tokenize_vdf('\\')) == [_Field('\\')]
assert list(_tokenize_vdf('\\n')) == [_Field('\n')]
assert list(_tokenize_vdf('\\t')) == [_Field('\t')]
assert list(_tokenize_vdf('\\"')) == [_Field('"')]
assert list(_tokenize_vdf('\\\\\\"')) == [_Field('\\"')]
assert list(_tokenize_vdf('\\\\')) == [_Field('\\')]
assert list(_tokenize_vdf('\\\\\\')) == [_Field('\\\\')]
assert list(_tokenize_vdf('\\\\\\\\')) == [_Field('\\\\')]
assert list(_tokenize_vdf('\\\\\\\\t')) == [_Field('\\\\t')]
assert list(_tokenize_vdf('\\\\\\\\\\t')) == [_Field('\\\\\t')]
assert list(_tokenize_vdf('"\\t\\n\\"\\\\\\\\\\"\\n\\t"')) == [
    _Field('\t\n\"\\\\\"\n\t')
]
assert list(_tokenize_vdf('"\\\\"\n"abc"')) == [_Field('\\'), _Field('abc')]

# Escape chars (disabled)
assert list(_tokenize_vdf('\\', escape=False)) == [_Field('\\')]
assert list(_tokenize_vdf('\\n', escape=False)) == [_Field('\\n')]
assert list(_tokenize_vdf('\\t', escape=False)) == [_Field('\\t')]

try:
    list(_tokenize_vdf('\\"', escape=False))
    assert False
except VDFConsistencyFailure as e:
    assert e.message == 'Mismatched quotes!'
    
try:
    list(_tokenize_vdf('\\\\\\"', escape=False))
    assert False
except VDFConsistencyFailure as e:
    assert e.message == 'Mismatched quotes!'
    
assert list(_tokenize_vdf('\\\\', escape=False)) == [_Field('\\\\')]
assert list(_tokenize_vdf('\\\\\\', escape=False)) == [_Field('\\\\\\')]
assert list(_tokenize_vdf('\\\\\\\\', escape=False)) == [_Field('\\\\\\\\')]
assert list(_tokenize_vdf('\\\\\\\\t', escape=False)) == [_Field('\\\\\\\\t')]
assert list(_tokenize_vdf('\\\\\\\\\\t', escape=False)) == [
    _Field('\\\\\\\\\\t')
]
assert list(_tokenize_vdf('"\\t\\n\\"\\\\\\\\\\"\\n\\t"', escape=False)) == [
    _Field('\\t\\n\\'), _Field('\\\\\\\\\\'), _Field('\\n\\t')
]
assert list(_tokenize_vdf('"\\\\"\n"abc"', escape=False)) == [
    _Field('\\\\'), _Field('abc')
]

# Bad VDF

try:
    list(_tokenize_vdf('"'))
    assert False
except VDFConsistencyFailure as e:
    assert e.message == 'Mismatched quotes!'
    
try:
    list(_tokenize_vdf('"abc def  {}   ""{ghi}""'))
    assert False
except VDFConsistencyFailure as e:
    assert e.message == 'Mismatched quotes!'
    
try:
    list(_tokenize_vdf('"""""'))
    assert False
except VDFConsistencyFailure as e:
    assert e.message == 'Mismatched quotes!'
    
# Comments
assert list(_tokenize_vdf('//')) == []
assert list(_tokenize_vdf('// abc')) == []
assert list(_tokenize_vdf('// abc def')) == []
assert list(_tokenize_vdf('// abc def\nghi')) == [_Field('ghi')]
assert list(_tokenize_vdf('/ abc def\nghi')) == [_Field('ghi')]
assert list(_tokenize_vdf('"/"')) == [_Field('/')]
assert list(_tokenize_vdf('/"')) == []

print "All tests passed!"

