# petalbear
Python code for loading ravelry one-use codes into Mailchimp merge fields

usage: petalbear [-h] [--config CONFIG] --ravcodes RAVCODES --campaign
                 CAMPAIGN

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -f CONFIG
                        Configuration file for petalbear, defaults to
                        ~/.petalbearrc
  --ravcodes RAVCODES, -r RAVCODES
                        CSV file from ravlery containing codes. No default.
  --campaign CAMPAIGN, -c CAMPAIGN
                        Name of ravelry campaign. No default.

Sample configuration file:

[mailchimp]
apikey = b2b1e11b8eb6fc1bc55b3790ca284a4a-usX
list_name = My Beta List
