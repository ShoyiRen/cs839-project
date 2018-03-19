
# coding: utf-8

# In[3]:


# Source: http://www.netinstructions.com/how-to-make-a-web-crawler-in-under-50-lines-of-python-code/
from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from urllib import request

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):

    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url, word):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
#         response = urlopen(url)
        #Source: https://stackoverflow.com/questions/3336549/pythons-urllib2-why-do-i-get-error-403-when-i-urlopen-a-wikipedia-page
        req = request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
        response = request.urlopen( req )
        
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        if response.getheader('Content-Type')=='text/html; charset=utf-8' or "text/html;charset=UTF-8":
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            instance = ""
            isbn = ""
            if word in htmlString:
        
                #find title and author
                index = htmlString.index("<title>")
                newString = htmlString[index+7:]
                index = newString.index("</title>")
                newString = newString[:index]
                index = newString.index(" |")
                newString = newString[:index]
                authorIndex = newString.rfind("by")
                title = newString[:authorIndex]
                title = title.strip()
                title = title.replace(",", "")
                author = newString[authorIndex:]
                author = author.replace(", Paperback", "")
                author = author.replace(", Hardcover", "")
                author = author[3:]
                author = author.replace(",", ";")
#                 print(title)
#                 print(author)
                
                if "ISBN-13:" in htmlString and "Format:" not in htmlString and "File size:" not in htmlString:
                    #find ISBN-13
                    index = htmlString.index("<td>")
                    temp = htmlString[index+4:]
                    index = temp.index("</td>")
                    isbn = temp[:index]
#                     print(isbn)
                    temp = temp[index:]
                    isbn = isbn.replace(",", "")
                    
                    #find publisher
                    index = temp.index("<td>")
                    temp = temp[index+4:]
                    index = temp.index(">")
                    temp = temp[index+1:]
                    index = temp.index("</a>")
                    publisher = temp[:index]
#                     print(publisher)
                    temp = temp[index:]
                    publisher = publisher.replace(",", "")
                    
                    #find publication date
                    index = temp.index("<td>")
                    temp = temp[index+4:]
                    index = temp.index("</td>")
                    pubDate = temp[:index]
#                     print(pubDate)
                    temp = temp[index:]
                    pubDate = pubDate.replace(",", "")
                    
                    #find series
                    series = ""
                    if "Series:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+4:]
                        index = temp.index(">")
                        temp = temp[index+1:]
                        index = temp.index("</td>")
                        series = temp[:index]
                        series = series.replace("</a>\n", "")
#                         print(series)
                        temp = temp[index:]
                        series = series.replace(",", "")

                    
                    #find edition description
                    ed = ""
                    if "Edition description:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+4:]
                        index = temp.index("</td>")
                        ed = temp[:index]
#                         print(ed)
                        temp = temp[index:]
                        ed = ed.replace(",", "")
                    
                    #find pages
                    pages = ""
                    if "Pages:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+4:]
                        index = temp.index("</td>")
                        pages = temp[:index]
#                         print(pages)
                        temp = temp[index:]
                        pages = pages.replace(",", "")
                        
                    #find sales rank
                    sr = ""
                    if "Sales rank:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+4:]
                        index = temp.index("</td>")
                        sr = temp[:index]
#                         print(sr)
                        temp = temp[index:]
                        sr = sr.replace(",", "")
                        
                    #find product dimensions:
                    pd = ""
                    if "Product dimensions:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+5:]
                        index = temp.index("</td>")
                        pd = temp[:index]
#                         print(pd)
                        temp = temp[index:]
                        pd = pd.replace(",", "")
                    
                    #find lexile
                    lexile = ""
                    if "Lexile:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+4:]
                        index = temp.index(" (")
                        lexile = temp[:index]
#                         print(lexile)
                        index = temp.index("</td>")
                        temp = temp[index:]
                        lexile = lexile.replace(",", "")
                        
                    #find age range
                    ar = ""
                    if "Age Range:" in temp:
                        index = temp.index("<td>")
                        temp = temp[index+4:]
                        index = temp.index("</td>")
                        ar = temp[:index]
#                         print(ar)
                        temp = temp[index:]
                        ar = ar.replace(",", "")
                    
                    instance = title + "," + author + "," + isbn + "," + publisher + "," + pubDate + "," + series + "," + ed + "," + pages + "," + sr + "," + pd + "," + lexile + "," + ar
            self.feed(htmlString)
            return instance, isbn, self.links
        else:
            return "",[]

# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def spider(url, word, maxInstance):  
    pagesToVisit = [url]
    pagesVisited = set([])
    isbnList = set([])
    instances = set([])
    numberVisited = 0
    foundWord = False
    
    file = open("instances.txt", "r")
    for line in file:
        prev = line.split(",")
        instances.add(prev[0])
        isbnList.add(prev[2])
    
    file = open("instances2.txt", "w")
    
    # The main loop. Create a LinkParser and get all the links on the page.
    # Also search the page for the word or string
    # In our getLinks function we return the web page
    # (this is useful for searching for the word)
    # and we return a set of links from that web page
    # (this is useful for where to go next)
    while len(instances) <= maxInstance and pagesToVisit != []:

        numberVisited = numberVisited +1
        # Start from the beginning of our collection of pages to visit:
        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        try:
            print(numberVisited, "Visiting:", url)
            parser = LinkParser()
            instance, isbn, links = parser.getLinks(url, word)
            if instance and (instance not in instances) and isbn and (isbn not in isbnList):
                print("added")
                isbnList.add(isbn)
                instances.add(instance)
                file.write(instance + "\n")
                
            pagesVisited.add(url)
            
            for link in links:
                if (link not in pagesVisited) and (link not in pagesToVisit) and ("www.barnesandnoble.com/w/" in link):
                    pagesToVisit.append(link)
        except Exception as e:
            print(e)
            print(" **Failed!**")
            
    file.close()

        
def main():
    # Mystery & Crime
#     url = "https://www.barnesandnoble.com/b/books/mystery-crime/_/N-8q8Z16g4?Nrpp=40&page=1"

    # Science Fiction & Fantasy
#     url = "https://www.barnesandnoble.com/b/books/science-fiction-fantasy/_/N-8q8Z180l?Nrpp=40&page=1"

    # Fiction
    url = "https://www.barnesandnoble.com/b/books/history/_/N-1fZ29Z8q8Z11km?Nrpp=40&page=1"
    kw = "Product Details"
#     kw2 = "Add to Wishlist"
    spider(url, kw, 4000)
    
if __name__ == "__main__":
    main()

