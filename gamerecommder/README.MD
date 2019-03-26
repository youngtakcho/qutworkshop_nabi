<H1>About This Project</H1>

<h2>What this project does?</h2>
<p>
The final goal of This project is making recommended game list based on user reviews from steam (over 1millon reviews).<br>
<br>
This project's demo is a search part of Game Recommender powered by genism.
Since the review data is over 2Gbytes, a brute force search method takes unacceptable time.
For solve this problem, the inverted index method is adopted.<br>
</p>
<h2>How is the data of reviews processed?</h2>

First, I store all data to a SQLite DB file to make easier to handle data with adding index numbers for review records. After storing data, other SQLite DB file is made to storing preprocessed data which is lemmatized and stemmed and does not have stop-words. First one is called original and second one is called preprocessed. Preprocessed DB is used for real processing and original DB is used for showing reviews to users.<br>
Second, the inverted index dictionary is need. It can be made with several steps with python.<br><br>
<div class="nintyning">
	<h3>steps to make inverted index dictionary</h3>
	<ul>
<li>1.	Select reviews and indices of them by using SQLite from preprocessed DB.</li><br>
<li>2.	Get a row from the results and Split the preprocessed review in words array.</li><br>
<li>3.	Store index of reviews in python set which is value of python dictionary and its key is the word in the word array. (python set does not accept duplicated data. By using set, I can store only word’s existence. Moreover, set is good for doing Boolean retrieval.) </li><br>
<li>4.	Do 2, 3 for all rows in SQL results.</li><br>
<li>5.	Store Dictionary to file by using pickle.</li><br><br>
</ul>
</div>
<p>
After this step, the Inverted index dictionary can be used for search. Once it is loaded to memory. We can do Boolean retrieval in in-memory manner. This makes good performance in time but needs a lot of memory to load dictionary.
My dictionary file size is over 300Mbytes this cannot be loaded in free hosting server since the space of server memory is too small. To solve this problem, I make home server and bind public domain name to my server by using Asus service which provide to all Asus router users.<br>
</p>
<h2>How is the query of search processed?</h2>

For search, the query must be processed in same way to preprocessed data (lemmatize, stemming, stop-words removal). After that the preprocessed query should be split in array and get sets of review indices from dictionary by using word to dictionary key. I do Boolean retrieval by using intersection method of python set. By intersecting all result sets, the Boolean retrieval is achieved.<br>
The result of intersecting sets is search results of the query. Since there are too many results, we have to rank results.
Boolean model TF-IDF method was used for ranking the reviews. It can be easily achieved with inverted index dictionary. IDF can be calculated by log (the number of rows in preprocessed DB/ size of value of dictionary) and we can get TF value by using Inverted index dictionary: there are reviews index whose key is query’s words and counting the word in a review from DB.
However, calculating TF-IDF took a lot of time and the similarity result with TF-IDF vectors is not acceptable (precision performance is poor and processing time is too long.)
Since its’ performance is poor, I use gensim Similarity library. It makes its’ own dictionary. Gensim offers several way to calculate similarity between query and data and use multi thread. <br>
Making genism dictionary takes long time and doing it for every query is not proper way. I re-write my data preprocessing code to save gensim dictionary at the same time when inverted index dictionary is saved.<br>
<br>
<h2>How does the server service this?</h2>
<p>
For making RESTful APIs, I use Flask which is a micro web framework written in Python. I open my home server’s port 5000 which is Flask default port and bind 80 port in router Port Forwarding setting menu; it binds outside port 80 and inside port 5000 with proper IP address changing.
When Flask starts up, the inverted index dictionary and genism dictionary are loaded from disk and it makes processing time for query acceptable.
Clients can ask a query to Flask server with HTTP protocol and server accept that and make a proper HTTP respond message as a result of the query.
When query from a client is received, the server preprocess that query as same way to reviews data from steam did be done. By using inverted index dictionary, find all reviews which have a word in the query. After collecting reviews, the server does Boolean retrieval using the set intersection method and calculates similarity between the query and reviews from intersection results. The top 100 result of calculating similarity can be responds to the client.</p>
<h2>What I fail and How to overcome it?</h2>
<div class="nintyning">
	<ul>
<li>1.	When I try to load inverted index and gensim dictionaries, Amazon EC2 server cannot load them due to insufficiency of memory.</li><br>
<ul><li>a.	Make a home server and add it to the Asus DNS server which is supported by Asus for its router buyers.</li></ul><br>
<li>2.	TF-IDF results is not good for service and it takes too much time.</li><br>
<ul><li>a.	Using Gensim library. It provides similarity class and parallel processing.</li></ul><br>
</ul>
</div>
<br>
<h2>What things to do next?</h2>
<div class="nintyning">
	<ul>
<li>1.	Making cached inverted index dictionary to fit low memory environments and move server to amazon EC2 server.</li><br>
<li>2.	Making a classifier. It will classify a user or game based on reviews and game genre to several groups.</li><br>
<li>3.	Making a recommender. It will make a recommend list of game. Based on review and game genre, the recommender selects games.</li><br>
</ul>
</div>
