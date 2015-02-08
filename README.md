# Stackoverflow bounty analysis
In this project we aim to analyse the influence of a bounty on a question. We 
will try to predict the time a question will get an answer after a bounty is set based on a preselected set of features.

## The Web Server
The project comes with a web server to present the prediction results for a given question. 

The Web Server relies on two data sources for its calculations:
1) The Stackoverflow REST API (10000 requests / day quota)
2) A Database with X tables contaning pre-calculated statistics on tag usage.
