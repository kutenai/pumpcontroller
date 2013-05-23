

import os

if os.environ.get("DEVELOPMENT",None):
    from dev import *

elif os.environ.get("TEST",None):
    from test import *

else:
    from prod import *


