#!/usr/bin/env python3.8
import requests
import json
import re
from datetime import datetime
from twisted.internet import task, reactor
from twisted.web.static import File
from twisted.web.server import Site

## This is a global list of all chasers that I manually compiled in json list format
## It should be called nsc_chasers.json in whatever directory your project is in.  
## I don't know why I am writing this, because I am the only one that will be hosting this probably.  
NSC_CHASERS = json.loads(open("nsc_chasers.json", "r").read())
OTHER_CHASERS = json.loads(open("other_chasers.json", "r").read())

## HTTP Port global variable
PORT = 80




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
    
    now = datetime.utcnow()
    pf = open('/var/www/html/nsc_gr.txt', 'w')
    pf.write('Refresh: 1\n')
    pf.write('Threshold: 999\n')
    pf.write(f'Title: Latest NSC Discord Chaser Locations (Last Updated: {now})\n')
    pf.write('Font: 1, 12, 0, "Courier New"\n')
    pf.write('IconFile: 1, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('IconFile: 2, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('IconFile: 6, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('IconFile: 7, 22, 22, 11, 11, "http://hldn.me/iconfile.png"\n')
    pf.write('All data provided by Spotter Network\n')
    pf.write('Historical location information is not tracked or stored\n')
    pf.write('Location data mirrors what is available from official Spoter Network feed\n')
    pf.write('With spotters that are not part of the NSC Discord filtered out, and cat icons\n')
    pf.write('You should still be able to use the official Spotter Network placefile along with this\n')
    pf.write('Questions or concerns, contact Holden Smith at h0lden.003@gmail.com\n\n')
    return pf


def update_placefile(placefile, name_display, location, icon):
    """
    Pass in our already initalized placefile object
    Add the 4 lines that make a spotter location
    """
    placefile.write(f"{location}\n")
    placefile.write(f"{icon}\n")
    placefile.write(f"{name_display}\n")
    placefile.write("End:\n\n")

    

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
            if sn_placefile[index + 2].startswith("Icon:"):
                icon_line = sn_placefile[index + 2]
                text_line = sn_placefile[index + 3]
            else:
                text_line = sn_placefile[index + 2]
                icon_line = sn_placefile[index + 1]
            name_pattern = r'(Icon:\s[0-9\,]*)"([\w\s\-\(\)\'\.]*)\\n(.*)'
            if match := re.search(name_pattern, icon_line):
                icon = match.group(1)
                chaser_name = match.group(2)
                the_rest = match.group(3)
                icon_number = icon.split(',')[4]
                new_icon_line = f'Icon: 0,0,000,7,{icon_number},"{chaser_name}\\n{the_rest}'
                if chaser_name in NSC_CHASERS:
                    print(f"[{datetime.utcnow()}]: {chaser_name} is a #TEAMREDMODE NSC_CHASER, adding them to custom placefile!")
                    icon_number = icon.split(',')[4]
                    new_icon_line = f'Icon: 0,0,000,7,{icon_number},"{chaser_name}\\n{the_rest}'
                    update_placefile(placefile=nsc_placefile, name_display=text_line, location=value, icon=new_icon_line)
                elif chaser_name in OTHER_CHASERS:
                    icon_number = icon.split(',')[4]
                    icon_number = str(int(icon_number) + 1)
                    new_icon_line = f'Icon: 0,0,000,7,{icon_number},"{chaser_name}\\n{the_rest}'
                    print(f"[{datetime.utcnow()}]: {chaser_name} is a PROMINENT, adding them to custom placefile!")
                    update_placefile(placefile=nsc_placefile, name_display=text_line, location=value, icon=new_icon_line)
    print("\n")


def event_loop():
    """
    This is the function that does all the work.  Put in its own function to make it easy to loop over.
    1) Grab SpotterNetwork Placefile
    2) Create a new NSC Placefile
    3) Loop over the data in the SpotterNetwork Placefile
    4) When we find data we need to use, add it to our placefile.
    """

    sn_placefile = get_sn()
    nsc_placefile = init_placefile()
    parse_sn(sn_placefile, nsc_placefile)
    

        

if __name__ == "__main__":
    timeout = 60.0
    l = task.LoopingCall(event_loop)
    l.start(timeout)
    resource = File('/var/www/html')
    factory = Site(resource)
    reactor.listenTCP(PORT, factory)
    reactor.run()
