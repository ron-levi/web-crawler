# web-crawler

Overview:
In this assignment i've implemented a concurrent basic web extraction application that given a list of websites urls extracts and prints logo image urls 
and phone numbers found on any of the given pages.
The program uses regular expression in order to generically locate phone numbers.
The program parses the html content of the pages and looks up img elements in which it fetches the image url from src attribute
in case it is a logo image.
Note: regex might be too permisive and catches non-valid numbers as well but it's pretty close :). Did not have time to fine tune the expression used.

Instructions:
To build: go to relevant directory where these files are saved and do docker build -t python-crawler .
then run: cat sites_examples.txt | docker run -i python-crawler
