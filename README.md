# Test scripts for OSINT

These scripts pull data from several sites and then plot the locations found on a Google Map.

## Usage

### Requirements

The most important requirement is __this script is written in Python 3.x__.

#### Modules

* bs4
* geocoder
* gmplot
* googlemaps
* requests

If you have PIP installed, type: `pip3 install -r requirements.txt` from the command line and your system should install all required modules.

#### Geocoding API

You will need to create a file named `geocode_api_keys.py` and put the following in it:

```bash
google_api_key = 'YOUR_GOOGLE_API_KEY'
bing_api_key = 'YOUR_BING_API_KEY'
```

Of course this means you need to go get a valid Google Developer API key for the Geocoding
(<https://developers.google.com/>).

You also can also create a Bing API key for free at <https://www.bingmapsportal.com/>. 

### Help command Output

#### Ratebeer.com

```bash
$  python ratebeer.py -h
usage: ratebeer.py [-h] -u USER

Grab ratebeer user activity

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Username to research
```

#### Yelp.com

```bash
$ python yelp_reviews.py -h
usage: yelp_reviews.py [-h] -u USER [--csv]

Grab yelp user activity

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Username to research
  --csv                 Output to CSV
```

### Example Output

#### Ratebeer.com

```bash
$ python ratebeer.py -u 105404
[ ] VENUE DATA: Requesting https://www.ratebeer.com/ajax/user/105404/place-ratings/1/1/
[ ] VENUE DATA: Requesting https://www.ratebeer.com/ajax/user/105404/place-ratings/2/2/
[ ] VENUE DATA: Requesting https://www.ratebeer.com/ajax/user/105404/place-ratings/3/3/
[ ] VENUE DATA: Requesting https://www.ratebeer.com/ajax/user/105404/place-ratings/4/4/
[ ] VENUE DATA: Requesting https://www.ratebeer.com/ajax/user/105404/place-ratings/5/5/
[ ] VENUE DATA: Requesting https://www.ratebeer.com/ajax/user/105404/place-ratings/6/6/

[ ] HTML output file named ratebeer_map_105404_1539303736.html was written to disk.
```

#### Yelp.com

```bash
python yelp_reviews.py -u U4gWrMtHevbDF3Le3GBLHA
[ ] VENUE DATA: Requesting https://www.yelp.com/user_details?userid=U4gWrMtHevbDF3Le3GBLHA
[ ] Can Geocode with Google.
[ ] VENUE DATA: Requesting https://www.yelp.com/user_details?userid=U4gWrMtHevbDF3Le3GBLHA&rec_pagestart=10
[ ] Can Geocode with Google.
[ ] VENUE DATA: Requesting https://www.yelp.com/user_details?userid=U4gWrMtHevbDF3Le3GBLHA&rec_pagestart=20
[ ] Can Geocode with Google.
[ ] VENUE DATA: Requesting https://www.yelp.com/user_details?userid=U4gWrMtHevbDF3Le3GBLHA&rec_pagestart=30

[-] No review addresses found

[ ] HTML output file named yelp_map_U4gWrMtHevbDF3Le3GBLHA_1539303863.html was written to disk.
```

All scripts should produce HTML output files that show the geolocated content. An example is below:
![image of sample output][example_output.png]

If your web page shows "For Development Purposes Only" watermarks, you will need to edit the HTML file and add your Google API key for JavaScript Maps API. Add `key=YOUR_GOOGLE_API_KEY` to the end of the maps.googleapis.com line like this: `https://maps.googleapis.com/maps/api/js?libraries=visualization&sensor=true_or_false&key=YOUR_GOOGLE_API_KEY`

## License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
