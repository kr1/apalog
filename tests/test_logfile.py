#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_logfile
----------------------------------

Tests for `logfile` module.
"""

import pytest
from collections import OrderedDict, Counter

from apalog import logfile, patterns


@pytest.fixture
def sample_log():
    return logfile.LogFile('tests/sample.log')


def test_instance_creation(sample_log):
    assert sample_log.count() == 100


def test_instance_creation_with_include_1():
    logs = logfile.LogFile('tests/sample.log', include_pattern='baidu')
    assert logs.count() == 15


def test_instance_creation_with_include_2():
    logs = logfile.LogFile('tests/sample.log', include_pattern='sound')
    assert logs.count() == 5


def test_instance_creation_with_exclude():
    logs = logfile.LogFile('tests/sample.log', exclude_pattern='baidu')
    assert logs.count() == 85


def test_OR(sample_log):
    assert sample_log.posAND(False).pos('baidu').pos('sound').count() == 20


def test_neg(sample_log):
    assert sample_log.neg('sound').count() == 95


def test_http_status(sample_log):
    assert sample_log.http_status(200).count() == 59


def test_classify_and_count(sample_log):
    expected = {'200': 59, '404': 27, '403': 2, '301': 2, '405': 1}
    assert sample_log.classify_and_count('HTTP/1.[10]" (...)') == expected


def test_count_status_codes(sample_log):
    expected = {'200': 59, '404': 27, '403': 2, '301': 2, '405': 1}
    assert sample_log.count_status_codes() == expected


def test_split_days(sample_log):
    expected = OrderedDict([('2015-09-01', 3), ('2015-09-02', 24)])
    assert sample_log.split_days().http_status(404).count() == expected


def test_classify_and_count_with_split_days(sample_log):
    expected = OrderedDict([
        ('2015-09-01', Counter({'200': 35, '301': 2, '403': 2, '404': 3})),
        ('2015-09-02', Counter({'200': 24, '404': 24, '405': 1}))])
    assert sample_log.split_days().classify_and_count('HTTP/1.[10]" (...)') == expected


def test_classify_and_count_IP_addresses(sample_log):
    expected = [('151.27.127.120', 36), ('206.99.94.219', 16), ('177.3.165.141', 5),
                ('199.58.86.209', 4), ('104.148.44.116', 2)]
    assert sample_log.classify_and_count(patterns.IP_V4_ADDRESS).most_common(5) == expected
