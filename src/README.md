# backend

## How to run

To boot up a server, simply run `python backend.py`. It will run on
localhost:5000

## CLI testing

For the moment (5/12/2014), you can get all questions like so. Note that at
the moment the `class_id` is ignored.

`curl -i http://localhost:5000/classes/c1234-1243/questions`

You can get a specific question by specifying the question id. Here is a
working example:

`curl -i http://localhost:5000/classes/c1234-1243/qustions/7d108fd4-9ac3-4a8e-9960-cb271f0de56b`

## Adding more functionality

I highly recommend [this tutorial](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)
to get up and running quickly.
