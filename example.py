#!/usr/bin/python
"""
    Author: Micah Hoffman (@WebBreacher)
    Purpose: To look up a user on yelp.com
"""

import argparse
from bs4 import BeautifulSoup
import geocoder
import gmplot
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time


####
# Functions
####

def get_mean(lst):
    return float(sum(lst) / len(lst))


# Parse command line input
parser = argparse.ArgumentParser(description="Grab yelp user activity")
parser.add_argument('-u', '--user', required=True, help='Username to research')
args = parser.parse_args()


def get_data_from_yelp(url):
    # Setting up and Making the Web Call
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/63.0'
        headers = {'User-Agent': user_agent}
        # Make web request for that URL and don't verify SSL/TLS certs
        response = requests.get(url, headers=headers, verify=False)
        return response.text

    except Exception as e:
        print('[!]   ERROR - yelp issue: {}'.format(str(e)))
        exit(1)


def get_user_data(passed_user):
    # Parsing user information
    url = 'https://www.yelp.com/user_details?userid={}'.format(passed_user)
    print("\n[ ] USER DATA: Requesting {}".format(url))
    resp = get_data_from_yelp(url)
    html_doc = BeautifulSoup(resp, "html.parser")
    #user1 = html_doc.find_all('span', 'stat')

    """ TODO
        <ul class="ylist">
                <li>
                    <h4>Location</h4>
    """

    if user1:
        return user1

# TODO - Get friend data from https://www.yelp.com/user_details_friends?userid=XXX

def yelp_pages(url):
    # This function retrieves location content by extracting <address>
    review_addresses = []
    reviewlatslongs = []
    resp = get_data_from_yelp(url)
    html_doc = BeautifulSoup(resp, "html.parser")
    addresses = html_doc.find_all('address')
    if addresses:
        for a in addresses:
            matchObj = re.search(r'\n\s+([a-zA-Z0-9].*)\s+<', str(a), re.M|re.I)
            review_addresses.append(matchObj.group(1).replace('<br/>', ', '))

        #print(review_addresses)
        for addy in review_addresses:
            g = geocoder.google(addy)
            if g:
                reviewlatslongs.append(tuple(g.latlng))
        return reviewlatslongs
    else:
        print('[-] No review addresses found')
        return False

def get_venue_data(passed_user):
    # Parsing check-in location information
    review_addresses = []
    reviewlatslongs = []
    url = 'https://www.yelp.com/user_details_reviews_self?userid={}'.format(passed_user)
    print("\n[ ] VENUE DATA: Requesting {}".format(url))
    reviewlatslongs = yelp_pages(url)

    # Try to make pulls for additional reviews
    for num in range(10, 5000, 10):
        url = 'https://www.yelp.com/user_details_reviews_self?userid={}&rec_pagestart={}'.format(passed_user, num)
        print("\n[ ] VENUE DATA: Requesting {}".format(url))
        reviewlatslongs1 = yelp_pages(url)
        if reviewlatslongs1:
            reviewlatslongs.extend(reviewlatslongs1)
        else:
            # If a false value came back, no addresses were found and we are done iterating
            break
    print(len(reviewlatslongs))
    print(reviewlatslongs)
    exit()
    review_lats, review_longs = zip(*reviewlatslongs)

    # Compute the center Lat and Long to center the map
    center_lat = get_mean(review_lats)
    center_long = get_mean(review_longs)
    gmap = gmplot.GoogleMapPlotter(center_lat, center_long, 6)

    # Create the points/heatmap/circles on the map
    """for lat, lng in reviewlatslongs:
        gmap.circle(lat, lng, 8000)
    gmap.scatter(drink_lats, drink_longs, '#FFFFFF', 8000, marker=False)"""
    for latlng, num, title in reviewlatslongstitle:
        try:
            gmap.marker(latlng[0], latlng[1], title='{} beers logged at {}'.format(num, title))
        except:
            pass
    gmap.heatmap(drink_lats, drink_longs, 1, 100)
    gmap.scatter(drink_lats, drink_longs, '#333333', size=20, marker=False)
    gmap.plot(drink_lats, drink_longs, '#FF33FF', edge_width=3)

    outfile = 'yelp_map_{}_{}.html'.format(args.user, str(int(time.time())))
    gmap.draw(outfile)
    print("\n[ ] HTML output file named {} was written to disk.\n".format(outfile))


###########################
# Start
###########################

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


###############
# Get Venue info
###############
venue = get_venue_data(args.user)
