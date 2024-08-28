#  <p align="center">Quakes</p>

![earthquakes >2.5 ](images/updated_events.png)

## Project Description
This project gets USGS data, cleans it, and displays it as either:

 * Jupyter notebook. `Quake_notes` is an all-in-one solution and the most instructive. It displays the map with folium because I wanted to recreate as closely as I could the USGS site which is done in Leaflet.JS and which Folium is based. 
 * Streamlit app. This uses `data_processing.py` to fetch the csv, format, and output the data as a parquet file.

<br><br>

# Table of Contents
- [Quakes](#quakes)
- [Project Description](#project-description)
- [Table of Contents](#table-of-contents)
- [Background](#background)
- [Status: 1st phase done.](#status-1st-phase-done)
  - [Phase 1 - Steps up to simple display](#phase-1---steps-up-to-simple-display)
  - [Phase 2 -  Pre-model development](#phase-2----pre-model-development)
  - [Phase 3 - Model development and display](#phase-3---model-development-and-display)
- [Understanding USGS Tsunami Data](#understanding-usgs-tsunami-data)
    - [Tsunami Event Validity (Valid values: -1 to 4)](#tsunami-event-validity-valid-values--1-to-4)
    - [Deaths from the Tsunami and the Source Event](#deaths-from-the-tsunami-and-the-source-event)
    - [Tsunami Cause Code: ](#tsunami-cause-code-)

 
# Background 
A few years ago I started a makerspace with a group of really good folks. Along the way, we met an artist and instructor, [Christina Weisner](https://www.christinaweisner.com/about), who was in the early stages of doing a project and consulting with one of our members, Kerry Krauss. Kerry was a professor of electronics technology at the local community college.

According to Kerry, the code was a bit of kludge. It got the data from USGS somehow; I'm not sure if was RSS, Atom, or JSON. From there, the data was processed and sent a signal to a bunch of Arduino Uno boards by *sound*. Each Arduino was used to actuate one of the seismometers Christina bought. That might seem nuts but Kerry's rationale was, since they were having to troubleshoot at each location, audio was easier to troubleshoot than whipping out a multimeter every time. You can see Christina & Kerry and learn more about her project [here](https://www.youtube.com/embed/uK_es620K0w).

What I liked about this project was how it blended art with technology. Even more interesting is one of the hydrophones was still functional so Christina (with some help) was able to make the observers part of the installation. Another thing I found interesting was the artist as a sort of conductor rather than as the sole author. Christina had the inspiration and idea but almost all the most fabrication and technical aspects came from others. 

[Top ](#table-of-contents)
<br><br>

# Status: 1st phase done.
[Top ](#table-of-contents)
<br>
## 1 - Steps up to simple display
 - [x] Pull JSON data from USGS of earthquakes greater than magnitude 2.5 over the last 24 hrs 
 - [x] Mung earthquake data
 - [x] Displays map of quakes >= 2.5 over last 24 hrs using Folium 

## 2 -  Deploy app
 - [ ] Deploy as app

## 3 -  Pre-model development
- [x] Contact Eric Geist at [Tsunami and Earthquake Research](https://www.usgs.gov/centers/pcmsc/science/tsunami-and-earthquake-research?qt-science_center_objects=0#qt-science_center_objects) to see if there have been more tsunami occurrences
- [x] Get & massage data for tsunami warnings and actual tsunamis reported
- [x] Dash app as an interim measure
- [ ] Contact Lisa Wald of USGS
- [ ] Get tsunami warning/occurrence data

## 4 - Model development and display
- [ ] Develop model
- [ ] Twilio integration
- [ ] Find a way to export a photo as .png rather than as `quakes_last_24_hours.html`
- [ ] Deploy and seek feedback
  
<br>
[Top ](#table-of-contents)
