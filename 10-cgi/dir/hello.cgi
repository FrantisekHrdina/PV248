#!/usr/bin/python3

import cgi

form = cgi.FieldStorage()

a = form.getvalue('a)
b = form.getvalue('b')

print("Content-type:text/plain\n\n")
print('Output of hello.cgi')
print('a=%s' % (a))
print('b=%s' % (b))
