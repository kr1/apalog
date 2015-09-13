===============================
Apalog
===============================


extract and aggregate data from apache logfiles


Features
--------

 * easy to use and read (fluent interface)


Getting Started
---------------

Installation
~~~~~~~~~~~~

#. clone the repo
#. run `pip install --user --editable .` from the project root (use --editable if you intend to make changes)

Usage
~~~~~

.. code:: python

    from apalog import logfile

    # create an instance of Logfile
    sample_log = logfile.LogFile('tests/sample.log')

    # full count
    assert sample_log.count() == 100

    # extract information, e.g. http_status
    assert sample_log.http_status(200).count() == 59

    # get the numbers of 404 requests by day
    expected = OrderedDict([('2015-09-01', 3), ('2015-09-02', 24)])
    assert sample_log.split_days().http_status(404).count() == expected

    # classify and count, e.g. HTTP Status
    expected = {'200': 59, '404': 27, '403': 2, '301': 2, '405': 1}
    assert sample_log.classify_and_count('HTTP/1.[10]" (...)') == expected

    # split in days
    expected = OrderedDict([
        ('2015-09-01', Counter({'200': 35, '301': 2, '403': 2, '404': 3})),
        ('2015-09-02', Counter({'200': 24, '404': 24, '405': 1}))])
    assert sample_log.split_days().classify_and_count('HTTP/1.[10]" (...)') == expected


License
---------

GPL version 3: http://www.gnu.org/licenses/gpl-3.0.en.html
