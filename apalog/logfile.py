# -*- coding: utf-8 -*-
"""Extract information from Apache logs."""

import re
import datetime
from collections import OrderedDict, Counter
from apalog.patterns import (HTTP_STATUS_TEMPLATE,
                             HTTP_STATUS_GROUP,
                             RESPONSE_SIZE,
                             DATE_PATTERN)


class LogFile():
    def __init__(self,
                 filepath,
                 include_pattern='',
                 exclude_pattern=''):
        with open(filepath) as logfile:
            include = include_pattern and re.compile(include_pattern)
            exclude = exclude_pattern and re.compile(exclude_pattern)
            loglines = [line for line in logfile
                        if ((not include_pattern or re.search(include, line))
                            and not (exclude_pattern and re.search(exclude, line)))]
        self.lines = loglines
        self.reset()

    def reset(self):
        self.rules = {'positive': [],
                      'positive_AND': True,
                      'negative': [],
                      'split_days': False,
                      'show_only': None}

    def __repr__(self):
        return str(self.rules)

    def all(self):
        res = self.__apply()
        self.reset()
        return res

    def count(self):
        applied = self.__apply()
        if type(applied) == OrderedDict:
            applied = OrderedDict(
                sorted([(key, len(value))
                        for key, value in applied.items()]))
        else:
            applied = len(applied)
        self.reset()
        return applied

    def __validate_line(self, line):
        return (((self.rules['positive_AND'] and
                 len([rule for rule in self.rules['positive']
                      if re.search(rule, line)]) == len(self.rules['positive']))
                 or
                 (not self.rules['positive_AND'] and
                 len([rule for rule in self.rules['positive'] if re.search(rule, line)]) > 0))
                and len([rule for rule in self.rules['negative'] if re.search(rule, line)]) == 0
                and (self.rules.get('content_gt') is None
                    or (re.search(RESPONSE_SIZE, line)
                        and int(re.search(RESPONSE_SIZE, line).groups()[0]) > self.rules['content_gt']))
                and (self.rules.get('content_lt') is None
                    or (re.search(RESPONSE_SIZE, line)
                        and int(re.search(RESPONSE_SIZE, line).groups()[0]) < self.rules['content_lt'])))

    def __apply(self):
        filtered = [line for line in self.lines if self.__validate_line(line)]
        if self.rules['split_days']:
            days = OrderedDict()
            date_pattern = re.compile(DATE_PATTERN)
            for line in filtered:
                date = re.search(date_pattern, line)
                if not date:
                    continue
                date = str(datetime.datetime.strptime(date.group(), "%d/%b/%Y").date())
                if days.get(date, False):
                    days[date].append(line)
                else:
                    days[date] = [line]
            filtered = days
            if self.rules['show_only']:
                newdict = OrderedDict()
                for date, lines in filtered.iteritems():
                    cut = self.__apply_show_only(self.rules['show_only'], lines)
                    if cut:
                        newdict[date] = cut
                filtered = newdict
        else:
            if self.rules['show_only']:
                filtered = self.__apply_show_only(self.rules['show_only'], filtered)
        return filtered

    def __apply_show_only(self, pat, lines):
        lines = [re.search(pat, line) for line in lines]
        return [(match.groups()[0] if match.groups() else match.group())
                for match in lines if match]

    def neg(self, val):
        self.rules['negative'].append(re.compile(val))
        return self

    def pos(self, val):
        self.rules['positive'].append(re.compile(val))
        return self

    def posAND(self, val):
        self.rules['positive_AND'] = val
        return self

    def http_status(self, status):
        self.rules['positive'].append(re.compile(HTTP_STATUS_TEMPLATE.format(status)))
        return self

    def content_gt(self, num_bytes):
        self.rules['content_gt'] = num_bytes
        return self

    def content_lt(self, num_bytes):
        self.rules['content_lt'] = num_bytes
        return self

    def split_days(self, val=True):
        self.rules['split_days'] = val
        return self

    def show_only(self, val):
        self.rules['show_only'] = re.compile(val)
        return self

    def classify_and_count(self, pat):
        '''applies rules, then uses the matching substring of <pat>

        to group and count occurrences.
        returns a dictionary of {substring:count} or
        an Ordered dict {date:{substring:count}} depending on the
        value of split_days'''

        pat = re.compile(pat)
        self.rules['show_only'] = pat
        applied = self.__apply()
        self.reset()
        if type(applied) == OrderedDict:
            new_dict = OrderedDict()
            for date, entry in sorted(applied.iteritems()):
                counted = Counter(entry)
                new_dict[date] = counted
            return new_dict
        else:
            return Counter(applied)

    def count_status_codes(self):
        return self.classify_and_count(re.compile(HTTP_STATUS_GROUP))

    def count_variants(self, pat):
        counted = self.classify_and_count(pat)
        if isinstance(counted, Counter):
            return len(counted)
        else:
            new_dict = OrderedDict()
            for date, entry in sorted(counted.iteritems()):
                length = len(entry)
                new_dict[date] = length
            return new_dict
