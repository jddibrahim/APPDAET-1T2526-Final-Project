## Instructions 
RUN the first cell of NewsArticleSearch.ipynb to download the important python modules on your environment before running the main cells.

## Important Documentations
1. World News API Search News Docs - https://worldnewsapi.com/docs/search-news/
2. ISO3166 Module Docs - https://pypi.org/project/iso3166/
3. Python-ISO639 Docs - https://pypi.org/project/python-iso639/

## For Developers

### Introduction
News Article Search App uses the World News API's data to generate article search results and display these to the user. Currently, there
is a console version available, and the current target is to integrate the Tkinter module of Python to use GUI to display these results 
like a search engine for the API. Additionally, MatPlotLib module will also be used to display how the number of articles for a certain search
query has grown over the years.

### FAQs
**1. Why run the first cell of NewsArticleSearch.ipynb before running or changing anything from this app before anything else?**

The World News API integrated in this app uses ISO3166 alpha-2 country codes (e.g. France -> 'FR') to specify the country the article is sourced from 
and ISO639-1 (alpha-2) language codes (e.g. English -> 'en') to specify the language used in the article. Rather than listing every country and language, and their
respective codes, these two Python modules were used to be able to automatically create a dictionary and a list of these codes through 
[list comprehension](https://www.w3schools.com/python/python_lists_comprehension.asp). 

**2. How can I easily select the data within the .json file of the API?**

Refer to the documentations link of [World News API](https://worldnewsapi.com/docs/search-news/) as guide on how to input the query parameters. Try it out on [Postman](https://www.postman.com/)
using the API key inside the *NewsArticleSearch.ipynb* file and see how the data are laid out in the .json file. By calling out the key values like how you would in Python dictionaries, you will
be able to access the respective values of they keys.

Example: 
Assuming that `data = response.json()` we can use the variable `data` to access the results of our query
<pre><code>  articles = []
  totalNum = data["available"]
  for entry in data["news"]:
    article = {
      "title": entry["title"],
      "author": entry["author"],
      "publish-date": entry["publish_date"],
      "language": entry["language"],
      "country": entry ["source_country"],
      "text": entry["text"],
      "url": entry["url"]
    }

    articles.append(article)
</code></pre>

**3. What features are still missing to complete the app?**

In its current state, the app is still in its *Console Version*. The app needs to have a *graphical user interface* (GUI) for abstraction to neatly **present
the search engine** so that it is more **user-friendly** and more **appealing to use**. To achieve this, we will be using the [Tkinter](https://realpython.com/python-gui-tkinter/)
module of Python. The app also needs to use [MatPlotLib](https://www.w3schools.com/python/matplotlib_intro.asp) to **plot the number of articles over time** for a particular
search query. 

**4. What are our targets for the Tkinter module and how should it be integrated?**

1. Creating the Window Interface
  - Create a Tkinter app class that gets generated/initialized every time the code is run
  - Creating the interface (from top to bottom):
    - Empty textbox / textfield to input the search query
    - 2 dropdown menus to fill unrequired fields selecting the language and source country of the articles
    - 2 buttons:
      - Search button - to execute the search query function and present the first 5 articles relevant to the query
      - Generate Search Trend - to generate a line graph to plot the number of articles over time of the query
    - A label that indicates how many articles are produced by the query 
    - 5 sets of search result labels for the info of each article:
      - Title
      - Author
      - Date Published
      - Country || Language
      - Text - first 250-300 characters (the developer decides) + ellipsis (...)
      - URL
    - 2 buttons to move the pages (next 5 articles, or previous 5 articles via manipulating the `offset` variable)
    - 2 buttons to skip to both ends (skip to the first page, or to the last page)
    - Page number (number of articles divided by 5)
2. Create the necessary functions to be called upon clicking the buttons
3. Attach the created functions to the buttons so that they are called whenever buttons are clicked

 **5. What are our targets for the MatPlotLib module and how should it be integrated?**

1. Create the data to plot
  - create data function
    - should create a list that stores the publish dates of the articles (through datetime module)
    - count the number of articles per date
2. Plot the data to the graph
  - create plot function to plot the data points (number of articles over time)
 


