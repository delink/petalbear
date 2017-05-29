# petalbear
Python code for loading ravelry one-use codes into Mailchimp merge fields

    usage: petalbear [-h] [-d] [-f CONFIG] -r RAVCODES -c CAMPAIGN

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable debug logging.
      -f CONFIG, --config CONFIG
                        Configuration file for petalbear, defaults to
                        ~/.petalbearrc
      -r RAVCODES, --ravcodes RAVCODES
                        CSV file from ravlery containing codes. No default.
      -c CAMPAIGN, --campaign CAMPAIGN
                        Name of ravelry campaign. No default.

    
Sample configuration file:
    
    [mailchimp]
    apikey = b2b1e11b8eb6fc1bc55b3790ca284a4a-usX
    list_name = My Beta List
