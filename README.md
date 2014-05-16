gnuclicker
==========

Gettign Started
==================

Prerequisites
-----------------

You will need python2.x, pip and virtualenv.

If you don't have pip (you can check just by typing pip in a shell), do:

sudo easy_install pip

If you don't have virtualenv (once you have pip) do:

sudo pip install virtualenv


Setting up the environment
---------------------------

From the root of the repo run 

./setup.sh

This will create a Python virtual environment, and install flask in it.


Developing/Running the code
--------------------------------

Before you begin developing, you must enter the virtual environment. You can do this by either running from the root of the repo

source flask/bin/activate
