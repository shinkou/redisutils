# Redis Utilities

## How To Use

### Install

Change to the `dist` directory and run the following command:

```
$ pip install .
```

### Run

#### Redis to CSV Extractor

To see the help page:

```
$ redis2csv -h
```

Or, to dump from Redis to CSV:

```
$ redis2csv -H some.redis.server -o /path/to/output/csv/file 'regexp_key_pattern_.*'
```

#### CSV to Redis Restorer

To see the help page:

```
$ csv2redis -h
```

To restore from CSV:

```
$ csv2redis -H some.redis.server /path/to/input/csv/file
```

#### Redis Keys Remover

To see the help page:

```
$ redisdel -h
```

To remove keys with RegExp patterns:

```
$ redisdel -H some.redis.server REGEXP1 [ REGEXP2 [ REGEXP3 ... ] ]
```

To remove keys provided in CSVs:

```
$ redisdel -H some.redis.server --csv CSV1 [ CSV2 [ CSV3 ... ] ]
```

### Run from the Docker Image

Issue the following command to run:

```
$ docker run -v "/dir/to/mount:/data" --rm -t shinkou/redisutils COMMAND
```
where _COMMAND_ is one of `redis2csv`, `csv2redis`, or `redisdel`.

### Prepare a Docker Image

You can also prepare your own Docker image if you feel adventurous. Simply
change to the top directory and run:

```
$ docker build -t TAG .
```
where _TAG_ can be simply *shinkou/redisutils*.
