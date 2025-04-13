Is my boss broke?
=================

This is a simple script that checks if your supervisor is broke.
It uses the NIH RePORTER APIs and the NSF APIs to check if your supervisor currently has any active grants.

Dependencies
------------
- requests

Usage
-----
You need to know your supervisor's first name, last name, and institution 
(as it appears in the NIH RePORTER and NSF databases, 
e.g., UNC-Chapel Hill is `'UNIV OF NORTH CAROLINA CHAPEL HILL'` in NIH RePORTER database
and is `'UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL'` in NSF database).

You can run the script with the following command:

```
usage: is_my_boss_broke.py [-h] --first FIRST --last LAST --institutions INSTITUTIONS

Search NIH RePORTER and NSF for projects with specified principal investigator and institution criteria.

options:
  -h, --help            show this help message and exit
  --first FIRST, -f FIRST
                        Exact first name of the principal investigator.
  --last LAST, -l LAST  Exact last name of the principal investigator.
  --institutions INSTITUTIONS, -i INSTITUTIONS
                        Comma-separated list of institution names (exact matches).
```

For example, if your supervisor's name is Sakiko Togawa, you would run:

```
python is_my_boss_broke.py -f Sakiko -l Togawa -i "HANEOKA GIRLS' HIGH SCHOOL, TSUKINOMORI GIRLS' ACADEMY"
```

provided that `"HANEOKA GIRLS' HIGH SCHOOL"` and `"TSUKINOMORI GIRLS' ACADEMY"` are the exact names of the institutions 
as they appear in the NIH RePORTER and NSF databases
.