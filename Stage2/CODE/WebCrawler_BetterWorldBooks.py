
# coding: utf-8

# In[30]:


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
            if "About the Book" in htmlString:        
                
                # find title and author and isbn
                index = htmlString.index("document.title")
                temp = htmlString[index+18:]

                index = temp.index("|")
                authorTitle = temp[:index].strip()
                authorIndex = authorTitle.rfind(" by ")
                title = authorTitle[:authorIndex].strip()
                title = title.replace(",", "")
                title = title.replace("\\", "")
                author = authorTitle[authorIndex+4:].strip()
                author = author.replace(",", ";")
                author = author.replace("\\", "")
                
                # find format and pages
                index = temp.index("<label>Format</label>")
                temp = temp[index:]
                index = temp.index("bookFormat")
                index2 = temp.index("</span>")
                formatPages = temp[index+12:index2]
                temp2 = formatPages.split(", ")
                form = temp2[0].replace(",", "")
                pages = ""
                if len(temp2) > 1:
                    pages = temp2[1].replace(",", "")
                
                #find language
                index = temp.index("<label>Language</label>")
                temp = temp[index:]
                index = temp.index("hidden-xs")
                temp = temp[index+11:]
                index2 = temp.index("</td>")
                language = temp[:index2].replace(",", "")

                #find publisher
                index = temp.index("<label>Publisher</label>")
                temp = temp[index+24:]
                index = temp.index("publisher")
                index2 = temp.index("</span>")
                publisher = temp[index+11:index2].replace(",", "")
                
                #find edition
                index = temp.index("<label>Edition</label>")
                temp = temp[index:]
                index = temp.index("bookEdition")
                index2 = temp.index("</span>")
                edition = temp[index+13:index2].replace(",", "")
                
                #find isbn-13
                index = temp.index("<label>ISBN-13</label>")
                temp = temp[index+22:]
                index = temp.index("isbn")
                index2 = temp.index("</span>")
                isbn13 = temp[index+6:index2].replace(",", "")
                
                #find dimensions
                index = temp.index("<label>Dimensions</label>")
                temp = temp[index:]
                index = temp.index("hidden-xs")
                temp = temp[index+11:]
                index2 = temp.index("</td>")
                dimension = temp[:index2].replace(",", "")
                
                #find isbn-10
                index = temp.index("<label>ISBN-10</label>")
                temp = temp[index+22:]
                index = temp.index("isbn")
                index2 = temp.index("</span>")
                isbn10 = temp[index+6:index2].replace(",", "")
                
                #find shipping weight
                index = temp.index("<label>Shipping Weight</label>")
                temp = temp[index:]
                index = temp.index("hidden-xs")
                temp = temp[index+11:]
                index2 = temp.index("</td>")
                weight = temp[:index2].replace(",", "")

                #find category
                index = temp.index("<label>Categories</label>")
                temp = temp[index:]
                index = temp.index("aspx")
                index2 = temp.index("</a>")
                category = temp[index+6:index2].replace(",", "")
                
#                 print(title)
#                 print(author)
#                 print(form)
#                 print(pages)
#                 print(language)
#                 print(publisher)
#                 print(edition)
#                 print(isbn13)
#                 print(dimension)
#                 print(isbn10)
#                 print(weight)
#                 print(category)
                
                instance = title + "," + author + "," + form + "," + pages + "," + language + "," + publisher + "," + edition + "," + isbn13 + "," + dimension + "," + isbn10 + "," + weight + "," + category
#             print(htmlString)

            self.feed(htmlString)
            return instance
        else:
            return ""

# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def spider(baseUrl, word):
    isbnList = set([])
    instances = set([])
    numberVisited = 0
    
    file = open("instances.txt", "r")
    for line in file:
        prev = line.split(",")
        isbnList.add(prev[2])
    
    file = open("examples.txt", "w")
    
    # The main loop. Create a LinkParser and get all the links on the page.
    # Also search the page for the word or string
    # In our getLinks function we return the web page
    # (this is useful for searching for the word)
    # and we return a set of links from that web page
    # (this is useful for where to go next)
    for isbn in isbnList:

        numberVisited = numberVisited +1
        # Start from the beginning of our collection of pages to visit:
        url = baseUrl + isbn

        try:
            print(numberVisited, "Visiting:", url)
            parser = LinkParser()
            instance = parser.getLinks(url, word)

            if instance and instance not in instances:
                file.write(instance + "\n")
                instances.add(instance)
                            
        except Exception as e:
            print(e)
            print(" **Failed!**")
            
    file.close()
        
def main():

    baseUrl = "https://www.betterworldbooks.com/product/detail/"
    kw = "Product Details"
    
    spider(baseUrl, kw)
    
if __name__ == "__main__":
    main()

