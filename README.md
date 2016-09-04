#whois_python
##Introduction
Some simple modules used to fetch domain information, and save them as .json files.
Module whois uses data from http://www.whois.com. 
Module awis uses data from http://www.alexa.com.

##Requirement
**python 3**

**requests** 2.1.0 + by Kenneth Reitz : https://github.com/kennethreitz/requests/

##Example
Fetch domain information about google.com:
```python
import whois
result = whois.who_is("google.com")
# result["Registrant"]["Organization"] should be "Google Inc."

import alexa
import json
info = alexa.get_domain_info("google.com")
print(json.dumps(info, indent=2))
# now the information fetched shall be printed out neetly and nicely.
```

##License
This module is distributed under the MIT license (https://opensource.org/licenses/MIT).

Copyright (c) 2016 Dasein Phaos

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.