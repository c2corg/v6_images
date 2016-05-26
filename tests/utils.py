import os
import pytest

skipIfTravis = pytest.mark.skipif(os.environ.get('TRAVIS', "false") == "true",
                                  reason="Not running on Travis")