#!/usr/bin/python
"""
    Author: Micah Hoffman (@WebBreacher)
    Purpose: To look up a user on yelp.com

    # Test users
    29 reviews = U4gWrMtHevbDF3Le3GBLHA
    52 reviews = 7Yn_ljl1SCd2br4NMFZkxA
    1333 reviews = 58yXn5Y4409kc9q88YwU6w
    TODO - 71 reviews = j5-CYwBPJMNFEnfg6aQ38Q (Canada...problem with geocoding)
"""

import argparse
from bs4 import BeautifulSoup
import csv
import geocoder
import gmplot
import random
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
parser = argparse.ArgumentParser(description="Grab yelp user activity")
parser.add_argument('-u', '--user', required=True, help='Username to research')
parser.add_argument('--csv', action="store_true", help='Output to CSV')
args = parser.parse_args()


def get_data_from_yelp(url):
    # Setting up and Making the Web Call
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/65.0'
        headers = {'User-Agent': user_agent}
        # Make web request for that URL and don't verify SSL/TLS certs
        response = requests.get(url, headers=headers, verify=False)
        return response.text

    except Exception as e:
        print('[!]   ERROR - yelp issue: {}'.format(str(e)))
        exit(1)

# TODO - Get user data
def get_user_data(passed_user):
    # Parsing user information
    url = 'https://www.yelp.com/user_details?userid={}'.format(passed_user)
    print("\n[ ] USER DATA: Requesting {}".format(url))
    resp = get_data_from_yelp(url)
    html_doc = BeautifulSoup(resp, "html.parser")

    """ TODO - Parse the content below
        <div class="user-profile_info arrange_unit">
                <h1>Kimberly &#34;Yelp Yoda&#34; S.</h1>
                    <h3 class="user-location alternate">Washington, DC</h3>
        <strong>4369</strong> Friends
        <strong>1333</strong> Reviews
        <strong>10344</strong> Photos
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

        # Test if we can geocode with Google or OpenStreetMap
        test_google = geocoder.google('1600 pennsylvania ave, washington, dc')
        if test_google.status == 'OVER_QUERY_LIMIT':
            goog = False
            print('[!] ERROR - Cannot Geocode with Google - OVER_QUERY_LIMIT. Trying OSM.')
            # Test if we can geocode with OpenStreetMaps
            test_osm = geocoder.osm('1600 pennsylvania ave, washington, dc')
            if test_osm.x:
                print('[ ] Can Geocode with OSM.')
                openstreet = True
            else:
                print('[!] ERROR - Cannot Geocode with OSM.')
                openstreet = False
        elif test_google.latlng:
            goog = True
        else:
            goog = False

        if goog == False and openstreet == False:
            print('[!] ERROR - Cannot geocode to Google or OpenStreetMap. Wait a while and re-run script.')
            exit(1)

        # At least one of the geocoders worked
        for addy in review_addresses:
            if goog:
                g = geocoder.google(addy)
                if g.latlng:
                    reviewlatslongs.append(tuple(g.latlng))
            elif openstreet:
                osm = geocoder.osm(addy)
                if osm.x:
                    #osm_combined = '{}, {}'.format(osm.x,osm.y)
                    #reviewlatslongs.append(osm_combined)
                    reviewlatslongs.append((osm.x,osm.y))

        #print(reviewlatslongs) # DEBUG
        return reviewlatslongs
    else:
        print('\n[-] No review addresses found')
        return False

def get_venue_data(passed_user):
    # Parsing check-in location information
    url = 'https://www.yelp.com/user_details?userid={}'.format(passed_user)
    print("[ ] VENUE DATA: Requesting {}".format(url))
    reviewlatslongs = yelp_pages(url)

    # Pause to prevent Yelp from shunning us
    time.sleep(random.random())
    # Try to make pulls for additional reviews
    for num in range(10, 5000, 10):
        url = 'https://www.yelp.com/user_details?userid={}&rec_pagestart={}'.format(passed_user, num)
        print("[ ] VENUE DATA: Requesting {}".format(url))
        reviewlatslongs1 = yelp_pages(url)
        # Pause to prevent Yelp from shunning us
        time.sleep(random.random())
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

    outfile = 'yelp_map_{}_{}.html'.format(args.user, str(int(time.time())))
    gmap.draw(outfile)
    print("\n[ ] HTML output file named {} was written to disk.".format(outfile))

    if csv:
        outfile = 'yelp_map_{}_{}.csv'.format(args.user, str(int(time.time())))
        print("[ ] CSV output file named {} was written to disk.".format(outfile))
        csv_data = []
        for row in reviewlatslongs:
            row1 = '{}, {}'.format(row[0], row[1])
            csv_data.append([passed_user, row1])
        with open(outfile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)

###########################
# Start
###########################

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


###############
# Get Venue info
###############
venue = get_venue_data(args.user)
