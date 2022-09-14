import requests
import string
from bs4 import BeautifulSoup
import os


# get the number of pages we want to scrape from the user
number_of_pages = int(input("Please, enter the number of pages to scrape: "))
article_type = input("Please, enter the article type: ")

default_working_directory = os.getcwd()

# webpage root to scrape
request_root = 'https://www.nature.com'

# the request url that consit in the root + articles section
request_url = f'{request_root}/nature/articles?sort=PubDate&year=2020'

# The request url for more pages
extra_page_request_url_part= f'{request_root}/nature/articles?searchType=journalSearch?sort=PubDate&year=2020&page=$page_number'



def change_to_default_working_directory():
    """Change to the default working directory"""
    os.chdir(default_working_directory)
    print(f'Working directory changed to {default_working_directory}')
    return True

def move_to_directory(working_directory):
    """Move to the working directory"""
    if os.access(working_directory, os.X_OK) and os.path.isdir(working_directory):
        os.chdir(working_directory)
        print(f'Working directory changed to {working_directory}')
        return True
    else:
        print(f'Error changing working directory to {working_directory}')
        return False

def request_page(page_number):
    """Request a page and return the response"""
    if page_number == 1:
        response = requests.get(request_url)
    else:
        extra_page_request_url = extra_page_request_url_part.replace('$page_number', str(page_number))
        response = requests.get(extra_page_request_url)
    return response

def parse_article(html_content, article_type = 'News'):
    """Parse the article html content and returns a tuple with the article title and the article content by using BeautifulSoup"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # get all articles from the page with <article> tag
    articles = soup.find_all('article')

    news_articles = []
    for article in articles:
        # articles of the "news" type will have a class of "c-meta__type" with value "news"
        if article.find('span', class_='c-meta__type') and article.find('span', class_='c-meta__type').text == article_type:
            # get the article url
            article_title_object = article.find('a', attrs={'itemprop': 'url'})
            article_url = article_title_object['href']
            print("href of the article is ", article_url)
            article_title = article_title_object.text

            # get the article content in another request to the article url
            article_response = requests.get(f'{request_root}{article_url}')
            if article_response:
                # if there is response, we create another BeautifulSoup object and get the text from it
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                article_content = article_soup.find('div', class_='c-article-body').get_text()

                # save the article text and title into a truple
                news_articles.append((article_title, article_content))
                
            else:
                print("Error getting article content")
                continue
        else:
            continue
    return news_articles

def create_page_number_directory(page_number):
    """Create a directory in the system for the current page number articles and returns the directory path or None if there is an error"""
    os.mkdir(f'Page_{page_number}')
    if os.access(f'Page_{page_number}', os.X_OK) and os.path.isdir(f'Page_{page_number}'):
        print(f'Page_{page_number} directory created')
        return os.path.join(os.getcwd(), f'Page_{page_number}')
    else:
        print(f'Error creating Page_{page_number} directory')
        return None

def save_articles_to_file(articles, directory_path):
    """Save the articles to a file in the directory path"""
    change_result = move_to_directory(directory_path)
    if change_result:
        # for each tuple in the list we will create a file and store the content
        for article in articles:
            # trim the article name 
            article_title = article[0].strip('\n\t')
            article_title = article_title.title()
            # remove special characters if there is
            for char in article_title:
                if char not in string.ascii_letters and char != ' ':
                    article_title = article_title.replace(char, '')

            # replace spaces with underscores
            article_title = article_title.replace(' ', '_')

            temp_file = open(f'{article_title}.txt', 'wb')
            # gets bytes from the article content
            temp_file.write(article[1].encode('utf-8'))
            temp_file.close()
            return True
    else:
        print(f'Error while saving articles due to error changing working directory to {directory_path}')
        return False

def start_scraping():
    """Initial function to start scraping"""
    if number_of_pages >= 1: # only make a request if at least 1 page is requested
        
        
        for page_number in range(1, number_of_pages + 1):
            # for each iteration we go back to the default working directory
            change_to_default_working_directory()
            # request the page
            response = request_page(page_number)
            if response:
                # if there is a 200 response, parse the article
                parsed_articles = parse_article(response.content, article_type)
                # create a directory for the page number
                page_number_directory = create_page_number_directory(page_number)
                scrapping_result = save_articles_to_file(parsed_articles, page_number_directory)
                if scrapping_result:
                    print(f'Articles saved to Page_{page_number_directory}')
                else:
                    print(f'Error saving articles to Page_{page_number_directory}')
            else:
                print('Error while requesting')
    else:
        print('Please, enter a number greater than 0')


def main():
    start_scraping()

if __name__ == "__main__":
    main()


