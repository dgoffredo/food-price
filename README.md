Supermarket Catalog Scraper
===========================
I've heard that supermarkets do clever things with their prices. Does my
supermarket do that?

This is a web scraper that organizes the entire catalog of a supermarket into a
SQLite database.

```console
$ ./install-dependencies
[...]
$ sqlite3 db.sqlite <schema.sql
$ mkdir scratch
$ ./scrape db.sqlite scratch
```

The last command can be repeated as a cron job. Then,

```console
$ sqlite3 db.sqlite
SQLite version 3.37.2 2022-01-06 13:25:41
Enter ".help" for usage hints.
sqlite> .mode columns
sqlite> .headers on
sqlite> select name, size, price from ScrapedCatalogEntry where name like '%chicken%' order by name desc limit 5;
name                                        size      price
------------------------------------------  --------  ----------
teresa's - Sweet Chicken Sausage Rope       16 OZ     $7.49 each
sylvia's - Crispy Fried Chicken Mix         10 OZ     $4.59 each
sw Chicken Chipotle                         10 OZ     $7.99 each
stouffer's - Chicken a la King              11.50 OZ  $6.29 each
stouffer's - Chicken Rst Rigatoni rb Pesto  8.38 OZ   $6.29 each
```
