# gog-better-discount-checker
## Usage
clone the repository `git clone https://github.com/Willow0349/gog-better-discount-checker.git`  
go into the local copy `cd gog-better-discount-checker`  
set the `COOKIE` environment variable it starts with `gog-al=` and is about 150 charaters long (include the `gog-al=` part).  
execute the script `./gog-better-discount-checker.py`

The script will print out a list of games with a better discount than what you paid for them.  
It will sometimes print ex. "Error! Product id: 1162551261" if it can not get the price (normally for delisted games or limited time bundles that are no longer available).
