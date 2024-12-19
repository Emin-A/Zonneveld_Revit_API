# -*- coding: utf-8 -*-
import sys
import platform
import math
import json

try:
    # Hardcoded pyRevit Version
    pyrevit_version = "4.8.16 (Hardcoded)"

    # Revit API Test
    revit_version = __revit__.Application.VersionNumber

    # Engine Detection
    if "IronPython" in sys.version:
        python_engine = "IronPython"
        python_version = "2.7.11 (Hardcoded)"
    else:
        python_engine = "CPython"
        python_version = "3.7.8 (Hardcoded)"

    # Math Library Test
    sqrt_test = math.sqrt(16)

    # JSON Library Test
    json_test = json.dumps({"Engine": python_engine, "Version": python_version})

    # Print Results
    print("===== pyRevit Compatibility Test =====")
    print("Revit Version: {}".format(revit_version))
    print("pyRevit Version: {}".format(pyrevit_version))
    print("Python Engine: {} ({})".format(python_engine, python_version))
    print("Math Library Test: sqrt(16) = {}".format(sqrt_test))
    print("JSON Library Test: {}".format(json_test))
    print("=====================================")

    print("Compatibility test completed successfully!")

except Exception as ex:
    print("Compatibility Test Failed: {}".format(ex))
