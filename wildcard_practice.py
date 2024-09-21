from fnmatch import *
# currently fnmatch only supports * ? [seq] [!seq] in wildcard pattern, so need to write
# some manually
pattern = "fr%nka"
a = fnmatch("franka", pattern)

# translate % and -  to * and ? in wildcard pattern into fnmatch recognizable
def translate_wildcard(pattern):
    pattern = pattern.replace('%', '*')
    pattern = pattern.replace('_', '?')
    return pattern
if a is False:
    pattern = translate_wildcard(pattern)
    print(fnmatch("franka", pattern))
    print
else:
    print(True)