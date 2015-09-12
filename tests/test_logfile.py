#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_logfile
----------------------------------

Tests for `logfile` module.
"""

import pytest
from collections import OrderedDict

from apalog import logfile


@pytest.fixture
def sample_log():
    return logfile.LogFile('tests/sample.log')


def test_instance_creation(sample_log):
    assert sample_log.count() == 100


def test_instance_creation_with_include():
    logs = logfile.LogFile('tests/sample.log', include_pattern='baidu')
    assert logs.count() == 15


def test_instance_creation_with_exclude():
    logs = logfile.LogFile('tests/sample.log', exclude_pattern='baidu')
    assert logs.count() == 85


def test_http_status(sample_log):
    assert sample_log.http_status(200).count() == 59


def test_status_frequency(sample_log):
    expected = {'200': 59, '404': 27, '403': 2, '301': 2, '405': 1}
    assert sample_log.classify_and_count('HTTP/1.[10]" (...)') == expected


def test_splt_days(sample_log):
    expected = OrderedDict([('2015-09-01', 3), ('2015-09-02', 24)])
    assert sample_log.split_days().http_status(404).count() == expected
