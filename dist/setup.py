#!/usr/bin/env python
# vim: ff=unix fileencoding=utf-8 lcs=tab\:>. list noet sc sw=4 ts=4 tw=0
from setuptools import setup
import unittest

def redisutils_test_suite():
	test_loader = unittest.TestLoader()
	test_suite = test_loader.discover('tests', pattern = 'test_*.py')
	return test_suite

setup(
	name = 'redisutils'
	, version = '0.1'
	, packages = ['redisutils']
	, scripts = ['bin/csv2redis', 'bin/redis2csv', 'bin/redisdel']
	, install_requires = ['redis']
	, author = 'Chun-Kwong Wong'
	, author_email = 'chunkwong.wong@gmail.com'
	, description = 'Redis Utilities'
	, url = 'https://github.com/shinkou/redisutils'
	, test_suite = 'setup.redisutils_test_suite'
)
