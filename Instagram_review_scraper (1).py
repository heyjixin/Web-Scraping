from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import math


#create a dataframe to store the reviews
instagram = pd.DataFrame(columns = ['companyName','datePublished','ratingValue','reviewBody'])


#query the first page to get total number of reviews, and number of reviews per page
url = 'https://www.trustpilot.com/review/instagram.com?page=1'
try:
	res = requests.get(url)
except:
	print('Failed')

html_text = res.text
soup = BeautifulSoup(html_text,'html.parser')


#get total number of reviews (ALL LANGUAGE)
total_reviews_raw = soup.find('span', attrs = {"class": "headline__review-count"})
total_reviews = int(total_reviews_raw.text.split()[0])

#get total number of reviews (ENGLISH ONLY)
total_ENG_reviews_raw = soup.find('script', attrs = {"type": "application/json", "data-initial-state":"review-list"})
total_ENG_reviews = json.loads(total_ENG_reviews_raw.contents[0])['totalNumberOfReviews']

#get all review cards in the page
review_cards = soup.find_all('div', attrs = {"class":"review-card"})

#count the total number of reviews per page in the first page: to determine how many pages to query
num_reviews_perPage = len(review_cards)

#determine the number of pages to query after the first page

"""ENGLISH REVIEWS ONLY"""
num_pages_left = math.ceil((total_ENG_reviews - num_reviews_perPage) / num_reviews_perPage)


#retrieve the review contents in each page, and insert each reviews with non-empty body to the dataframe
def get_reviews_in_page(reviewCards, df):
	#iterate through all review cards in the page
	for card in reviewCards:
		#if the review body is empty (i.e. the review only has a title), skip it
		review_body = card.find('p', attrs = {"class":"review-content__text"})
		if isinstance(review_body,type(None)):
			continue
		else:
			reviewBody = review_body.get_text(strip = True)

			#get date published
			review_dates = card.find('script', attrs = {"type":"application/json","data-initial-state":"review-dates"})
			datePublished = json.loads(review_dates.contents[0])['publishedDate']
			
			#get rating value
			star_rating = card.find('div', attrs = {"class":"star-rating star-rating--medium"})
			ratingValue = star_rating.contents[1].get('alt')[0]

			df = df.append({'companyName':'Instagram', 'datePublished':datePublished, 'ratingValue': ratingValue, 'reviewBody': reviewBody}, ignore_index = True)

	return df

#put the reviews in the first page into the dataframe
instagram = get_reviews_in_page(review_cards, instagram)


#iterate through the remaining pages and insert the reviews in the dataframe
for i in range(num_pages_left):
	page_num = i + 2
	url = 'https://www.trustpilot.com/review/instagram.com?page=' + str(page_num)

	try:
		res = requests.get(url)
	except:
		print('Failed')

	html_text = res.text

	soup = BeautifulSoup(html_text,'html.parser')

	review_cards = soup.find_all('div', attrs = {"class":"review-card"})

	instagram = get_reviews_in_page(review_cards, instagram)

#output the entire dataframe to csv file in the working directory
instagram.to_csv('instagramReviews.csv', index=False)
