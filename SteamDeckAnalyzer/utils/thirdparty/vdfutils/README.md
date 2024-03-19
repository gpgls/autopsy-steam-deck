VDFUtils
==========

Copyright © 2015 by DKY (Ryan Lam)

__VDFUtils__ is a Python utility library that provides the ability to parse and format data in Valve Data Format ("VDF", otherwise known as "[Valve KeyValues Format](https://developer.valvesoftware.com/wiki/KeyValues)").

Current version: ___3.0.1___

### Requirements
* Python 2.7

### Usage
The two main functions that are provided by _VDFUtils_ are `parse_vdf()` and `format_vdf()`. `parse_vdf()` is used to convert a VDF-formatted string into a Python `OrderedDict`, and `format_vdf()` is used to convert a Python `dict` into a VDF-formatted string.

_____

##### `parse_vdf(inData, allowRepeats=False, escape=True)`

###### Parameters
- `inData` - A VDF-formatted string.
- `allowRepeats` (default: `False`) - If this is `True`, duplicate keys in the VDF data will be collected into a list representing all of the keys' values. Otherwise, duplicate keys that occur later in the data will overwrite earlier keys.
- `escape` (default: `True`) - If this is `True`, the following special character sequences will be escaped and replaced with their character equivalents: `\\`, `\n`, `\t`, `\"`. Otherwise, these character sequences are interpreted literally.

###### Return Value
- A Python `OrderedDict` representing the parsed VDF data.

###### Exceptions
- `VDFConsistencyError` - Raised if the VDF data cannot be parsed.

_____

##### `format_vdf(data, escape=True)`
Takes dictonary data and returns a string representing that data in VDF format. If this cannot be done, raises `VDFSerializationError`.

###### Parameters
- `data` - Any Python `dict`.
- `escape` (default: `True`) - If this is `True`, all backslashes, newlines, tabs, and double quotes will be escaped and replaced with their escape sequence equivalents: `\\`, `\n`, `\t`, `\"`. Otherwise, the affected characters are directly inserted into the VDF-formatted data.

###### Return Value
- A string representing the serialized data in VDF format.

###### Exceptions
- `VDFSerializationError` - Raised if the data cannot be serialized.
