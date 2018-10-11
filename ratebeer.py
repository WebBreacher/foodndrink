#!/usr/bin/python
"""
    Author: Micah Hoffman (@WebBreacher)
    Purpose: To look up a user on ratebeer.com

    # Test users
    105404 5/5
    11116 6/6
"""

import argparse
from bs4 import BeautifulSoup
import geocoder
import googlemaps
import gmplot
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
from geocode_api_keys import *


####
# Functions
####

def get_mean(lst):
    return float(sum(lst) / len(lst))


# Parse command line input
parser = argparse.ArgumentParser(description='Grab ratebeer user activity')
parser.add_argument('-u', '--user', required=True, help='Username to research')
args = parser.parse_args()


def get_data_from_ratebeer(url):
    # Setting up and Making the Web Call
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0'
        headers = {'User-Agent': user_agent}
        # Make web request for that URL and don't verify SSL/TLS certs
        response = requests.get(url, headers=headers, verify=False)
        return response.text

    except Exception as e:
        print('[!]   ERROR - ratebeer issue: {}'.format(str(e)))
        exit(1)

# TODO - Get user data
def get_user_data(passed_user):
    # Parsing user information
    url = 'https://www.ratebeer.com/ajax/user/{}/'.format(passed_user)
    print("\n[ ] USER DATA: Requesting {}".format(url))
    resp = get_data_from_ratebeer(url)
    html_doc = BeautifulSoup(resp, "html.parser")

    """ TODO - Parse the content below
        <div class="user-profile_info arrange_unit">
                <h1>Kimberly &#34;ratebeer Yoda&#34; S.</h1>
                    <h3 class="user-location alternate">Washington, DC</h3>
        <strong>4369</strong> Friends
        <strong>1333</strong> Reviews
        <strong>10344</strong> Photos
    """

    if user1:
        return user1

# TODO - Get friend data from https://www.ratebeer.com/user_details_friends?userid=XXX

def ratebeer_pages(url):
    # This function retrieves location content by extracting <address>
    entry = []
    review_addresses = []
    reviewlatslongs = []
    gmaps = googlemaps.Client(key=google_api_key)
    black_list = ['Location', 'Avg', 'Score', 'Date', 'next >', 'last >>', '< prev']
    resp = get_data_from_ratebeer(url)
    html_doc = BeautifulSoup(resp, 'html.parser')
    addresses = html_doc.find_all('a')
    if addresses:
        for a in addresses:
             if a.string in black_list or a.string == None:
                 continue
             else:
                 entry.append(a.string)
        counter = 1
        for e in entry:
            if counter == 1:
                placename = e
                counter += 1
            elif counter == 2:
                country = e
                counter += 1
            elif counter == 3:
                region = e
                counter += 1
            elif counter == 4:
                city = e
                review_addresses.append('{}, {}, {}, {}'.format(placename, city, region, country))
                counter = 1

        for addy in review_addresses:
            g = gmaps.geocode(addy)
            if g[0]['geometry']['location']:
                loc = g[0]['geometry']['location']['lat'], g[0]['geometry']['location']['lng']
                reviewlatslongs.append(tuple(loc))
            else:
                continue
        return reviewlatslongs
    else:
        print('\n[-] No additional entries found')
        return False

def get_venue_data(passed_user):
    # Parsing check-in location information
    review_addresses = []
    reviewlatslongs = []
    url = 'https://www.ratebeer.com/ajax/user/{}/place-ratings/1/1/'.format(passed_user)
    print('[ ] VENUE DATA: Requesting {}'.format(url))
    reviewlatslongs = ratebeer_pages(url)

    # Try to make pulls for additional reviews
    for num in range(2, 100, 1):
        url = 'https://www.ratebeer.com/ajax/user/{}/place-ratings/{}/{}/'.format(passed_user, num, num)
        print('[ ] VENUE DATA: Requesting {}'.format(url))
        reviewlatslongs1 = ratebeer_pages(url)
        if reviewlatslongs1:
            reviewlatslongs.extend(reviewlatslongs1)
        else:
            # If a false value came back, no addresses were found and we are done iterating
            break

    review_lats, review_longs = zip(*reviewlatslongs)

    # Compute the center Lat and Long to center the map
    center_lat = get_mean(review_lats)
    center_long = get_mean(review_longs)
    gmap = gmplot.GoogleMapPlotter(center_lat, center_long, 6)
    gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
    # Create the points/heatmap/circles on the map
    gmap.heatmap(review_lats, review_longs, 1, 100)
    gmap.scatter(review_lats, review_longs, '#333333', size=1, marker=True)
    gmap.plot(review_lats, review_longs, '#FF33FF', edge_width=1)

    outfile = 'ratebeer_map_{}_{}.html'.format(args.user, str(int(time.time())))
    gmap.draw(outfile)
    print('\n[ ] HTML output file named {} was written to disk.\n'.format(outfile))


###########################
# Start
###########################

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


###############
# Get Venue info
###############
get_venue_data(args.user)
