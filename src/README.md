# backend

## How to run

To boot up a server, simply run `python backend.py`. It will run on
localhost:5000

If you need to install any missing packages, run (from the root directory) 
`pip install -r requirements.txt`.

To create & populate the database, run `db_create` followed by 
`db_dummy_populate`. One way of deleting the entire DB is to simply remove the
file that SQLite uses to store the data `rm gnuclicker.db`.
