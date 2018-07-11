## Description    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Application for connecting and executing queries in SQLite3 and PostgreSQL.  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; You can test application using database Chinook_Sqlite.sqlite.

## Installing  
```shell
$ pip install -r requirments.txt
$ sudo apt-get install python3-pyqt5 pyqt5-dev-tools 
```

## Examples
### SQLite3 example
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Connection string:
```shell
Chinook_Sqlite.sqlite
``` 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Query:
```shell
SELECT * FROM Artist;
``` 
### PostgreSQL example
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Connection string:
```shell
dbname='database' user='testuser' host='localhost' password='password'
``` 
