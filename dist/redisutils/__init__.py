# vim: ff=unix fileencoding=utf-8 lcs=tab\:>. list noet sc sw=4 ts=4 tw=0
import argparse, csv, re, redis, sys, tempfile


_statusline = lambda s: print("\r\x1b[2K%s" % (s), end='', flush=True)
_green = lambda s: '\x1b[1;32m%s\x1b[0m' % (s)
_white = lambda s: '\x1b[1;37m%s\x1b[0m' % (s)


def _connect(attrs):
	'''
	Create and return connection to Redis host with given attributes
	'''
	cnxinfo = {k: attrs[k] for k in ('host', 'port', 'db', 'charset', 'decode_responses') if k in attrs and attrs[k] is not None}
	return redis.Redis(**cnxinfo)


def _dump(redishost, regexps, csvwriter, lmt, scansize, show_status=False):
	'''
	Select and dump key-value pairs from Redis to CSV
	'''
	cnt = 0
	ks = []
	for k in redishost.scan_iter(count=scansize):
		for regexp in regexps:
			if regexp.match(k):
				ks += [k]
				cnt += 1
				if show_status:
					_statusline('%s keys found.' % (_white(cnt),))
				break
		if len(ks) >= scansize:
			vs = redishost.mget(ks)
			for i in range(0, len(ks)):
				csvwriter.writerow([ks[i], vs[i]])
			ks = []
			vs = None
		if 0 < lmt and lmt <= cnt:
			break
	if len(ks) > 0:
		vs = redishost.mget(ks)
		for i in range(0, len(ks)):
			csvwriter.writerow([ks[i], vs[i]])
	if show_status:
		print("\n%s\n" % (_green('Done!'),))


def _restore(redishost, csvreader, msetsize):
	'''
	Restore key-value pairs from CSV to Redis
	'''
	mapping = {}
	mapping_size = 0
	cnt = 0
	for r in csvreader:
		if 1 < len(r):
			mapping[r[0]] = r[1]
			mapping_size += 1
			if msetsize <= mapping_size:
				redishost.mset(mapping)
				cnt += mapping_size
				_statusline('%s records restored.' % (_white(cnt),))
				mapping = {}
				mapping_size = 0
	if 0 < mapping_size:
		redishost.mset(mapping)
		cnt += mapping_size
		_statusline('%s records restored.' % (_white(cnt),))
	print("\n%s\n" % (_green('Done!'),))


def _delete(redishost, ks):
	'''
	Delete specified keys from Redis
	'''
	cnt = 0
	for k in ks:
		redishost.delete(k)
		cnt += 1
		_statusline('%s keys deleted.' % (_white(cnt),))
	print("\n%s\n" % (_green('Done!'),))


def redis_argparser(description):
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument(
		'-H', '--host'
		, metavar='FQDN'
		, type=str
		, help='source host (default: "localhost")'
		, default='localhost'
	)
	parser.add_argument(
		'-P', '--port'
		, metavar='PORT'
		, type=int
		, help='source port (default: 6379)'
		, default=6379
	)
	parser.add_argument(
		'-D', '--db'
		, metavar='DB'
		, type=int
		, help='source database (default: 0)'
		, default=0
	)
	parser.add_argument(
		'--charset'
		, metavar='CHARSET'
		, type=str
		, help='decode charset (default: "utf-8")'
		, default='utf-8'
	)
	parser.add_argument(
		'--decode-responses'
		, metavar='BOOL'
		, type=bool
		, help='whether to decode responses (default: True)'
		, default=True
	)
	return parser


def redis_dump(attrs):
	'''
	Dump keys specified by given RegExps
	'''
	rhost = _connect(attrs)
	regexps = [re.compile(s) for s in attrs['pattern']]
	if attrs['output'] is not None:
		with open(attrs['output'], 'w') as f:
			_dump(rhost, regexps, csv.writer(f), attrs['limit'], attrs['count'], True)
	else:
		_dump(rhost, regexps, csv.writer(sys.stdout), attrs['limit'], attrs['count'])


def redis_restore(attrs):
	'''
	Restore entries from CSV
	'''
	rhost = _connect(attrs)
	for fpath in attrs['inputs']:
		with open(fpath, 'r') as f:
			_restore(rhost, csv.reader(f), attrs['mset_size'])


def redis_delete(attrs):
	'''
	Delete keys from CSV
	'''
	rhost = _connect(attrs)
	if attrs['csv']:
		for fpath in attrs['inputs']:
			with open(fpath, 'r') as f:
				_delete(rhost, [r[0] for r in csv.reader(f) if 0 < len(r)])
	else:
		regexps = [re.compile(s) for s in attrs['inputs']]
		with tempfile.TemporaryFile(mode='w+') as f:
			_dump(rhost, regexps, csv.writer(f), -1, 65536)
			f.seek(0)
			_delete(rhost, [r[0] for r in csv.reader(f) if 0 < len(r)])
