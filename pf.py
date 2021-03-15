#!/usr/bin/env python3.8
import requests
import json
import re
import time

## This is a global list of all chasers that I manually compiled in json list format
## It should be called nsc_chasers.json in whatever directory your project is in.  
## I don't know why I am writing this, because I am the only one that will be hosting this probably.  
NSC_CHASERS = json.loads(open("nsc_chasers.json", "r").read())

def get_sn():
    """
    Get the actual Spotter Network Data and then make a list of lines 
    This is a little bit ugly, but so is the placefile format..
    I accept pull requests.
    """
    r = requests.get("https://www.spotternetwork.org/feeds/gr.txt")
    return r.text.splitlines()



def init_placefile():
    """
    Initalize our placefile with some basic information in it
    I use a stupid iconfile to try to make people laugh.
    I can use the real ones if people complain about the catt
    """
    
    pf = open('/var/www/html/nsc_gr.txt', 'w')
    pf.write('Title: Latest NSC Discord Chaser Locations\n')
    pf.write('Refresh: 1\n')
    pf.write('Font: 1, 11, 0, "Courier New"\n')
    pf.write('IconFile: 1, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('IconFile: 2, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('IconFile: 6, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('IconFile: 7, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('Threshold: 999\n')
    pf.write('\n')
    return pf


def update_placefile(placefile, name_display, location, icon):
    """
    Pass in our already initalized placefile object
    Add the 4 lines that make a spotter location
    """
    placefile.write(f"{location}\n")
    placefile.write(f"{icon}\n")
    placefile.write(f"{name_display}\n")
    placefile.write("End:\n")

    

def parse_sn(sn_placefile, nsc_placefile):
    """
    This is where the (gross) magic happens
    I will have to continue to improve upon this, but for now it works.
    The spotter network placefile format is static, and we can assume each spotter is 4 lines
    Object: (lat, ng) - this is where it puts your dot
    Icon: This is icon, and information when you hover over icon
    Text: This is the text that shows the spotter name on the top
    """
    for index, value in enumerate(sn_placefile):
        if value.startswith("Object:"):
            icon_line = sn_placefile[index + 1]
            text_line = sn_placefile[index + 2]
            name_pattern = r'Icon:\s[0-9,]*"([A-z \(\)0-9]*)\\n'
            if match := re.search(name_pattern, icon_line):
                chaser_name = match.group(1)
                if chaser_name in NSC_CHASERS:
                    print(f"{chaser_name} is a #TEAMREDMODE NSC_CHASER, adding them to custom placefile!")
                    update_placefile(placefile=nsc_placefile, name_display=text_line, location=value, icon=icon_line)




if __name__ == "__main__":
    sn_placefile = get_sn()
    nsc_placefile = init_placefile()
    parse_sn(sn_placefile, nsc_placefile)







