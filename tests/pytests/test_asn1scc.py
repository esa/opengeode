#!/usr/bin/env python3

from opengeode import Asn1scc as asn1scc
asn1scc.LOG.setLevel(asn1scc.logging.DEBUG)

def test_1():
    ''' Test the call to asn2dataModel with one asn1 file '''
    result = asn1scc.asn2dataModel(['data/dv1.asn'])
    assert result is not None


def test_2():
    ''' Test the call to asn2dataModel with two asn1 files '''
    result = asn1scc.asn2dataModel(['data/dv1.asn', 'data/dv2.asn'])
    assert result is not None

if __name__ == '__main__':
    for name, value in dict(globals()).items():
        if name.startswith('test_'):
            print('---- Executing {} ----'.format(name))
            value()
            print('---- Done - {} ----\n'.format(name))
