How to Run the Tests
====================
If you have already installed behave and selenium, all you need to do is run
behave from the commandline

`behave`

How to Syntax Highlight
======================

For documentation, we want pretty highlighting in HTML that we can copy-paste
into Google Docs. Unfortunately, options on the web were lacking, so Ben
hacked this up. 

To use it, simply copy-paste all the features into the JS fiddle at 
http://jsfiddle.net/WEDt9/2. You may want to do something like:

For a Mac: 

`cat *.feature | pbcopy` 

On Ubuntu:

`cat *.feature | xclip -selection clipboard`

In Windows Powershell:

`cat *.feature | clip`

*NOTE:* This is extremely lazy, and it inserts extraneous `</span>`s. As far
as I know, this won't negatively affect anything, but it is frowned upon.
