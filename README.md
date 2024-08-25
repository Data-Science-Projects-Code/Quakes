#  <p align="center">Quakes</p>

![earthquakes >2.5 ](images/updated_events.png)

## TL;DR:
This project gets USGS data, cleans it, and displays it. The code itself can be run in three different ways, two of which output to Dash; one is a self-contained notebook. Pick whichever one matches your interest/expertise but realize that most work is currently being done on `dashboard.py` and `Quakes_single.py`.<br>
 * Jupyter notebook. `Quake_notes` is an all-in-one solution. Step through the code, see some of the thinking involved and see the quakes display with a folium map.
 * Single data prep file. `Quakes_single.py` is a terse single pandas file. Output is `quakes_last_24_hours.html` (for now) in the `/images`
folder and `quakes_last_24.pkl` in the `/data` folder. Use Dashboard.py to display to display.
 * `Dashboad.py` displays the quakes with Plotly Dash.
 * `Quakes_multi.py` is a set of modules that outputs the same as the Quakes_single.py file. It's currently lagging a bit behind.

<br><br>

# Table of Contents
- [Quakes](#quakes)
  - [TL;DR:](#tldr)
- [Table of Contents](#table-of-contents)
- [Background](#background)
- [Project Description](#project-description)
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

# Project Description
I want to take this in a somewhat different direction. In part, this is because I'd like to take a stab at a tsunami warning system. But part is simply because I don't have any hydrophones or for that matter anywhere to store them.

So, the plan (other than stepping into it as time permits) is to do a web app which I may or may not deploy. I'd like it to add some additional features like the tsunami model or meta-model. I'm probably going to do some of the analysis in SQL by way of [datasette](https://datasette.io/) and possibly [dogsheep beta](https://dogsheep.github.io/) I don't know either of these but Simon Willison seems like a top-notch guy and playing with new tech is what this is all about.

[Top ](#table-of-contents)
<br><br>

# Status: 1st phase done.
[Top ](#table-of-contents)
<br>
## Phase 1 - Steps up to simple display
 - [x] Pull JSON data from USGS of earthquakes greater than magnitude 2.5 over the last 24 hrs. 
 - [x] Mung earthquake data.
 - [x] Displays map of quakes >= 2.5 over last 24 hrs using Folium because I wanted to recreate as close as I could the USGS map which is done in Leaflet.JS, which Folium is based on. 

## Phase 2 -  Pre-model development
- [x] Contact Eric Geist at [Tsunami and Earthquake Research](https://www.usgs.gov/centers/pcmsc/science/tsunami-and-earthquake-research?qt-science_center_objects=0#qt-science_center_objects) to see if there have been more tsunami occurrences
- [x] Get & massage data for tsunami warnings and actual tsunamis reported
- [x] Dash app as an interim measure
- [ ] Contact Lisa Wald of USGS
- [ ] Get tsunami warning/occurrence data

## Phase 3 - Model development and display
- [ ] Develop model
- [ ] Twilio integration
  - [ ] Learn Twilio API
- [ ] Find a way to export a photo as .png rather than as `quakes_last_24_hours.html`
- [ ] Deploy and seek feedback
  
<br>

[Top ](#table-of-contents)
<br><br>


# Understanding USGS Tsunami Data
Just to be clear, this is about tsunamis and not earthquakes. I have it here for the next phase of the project. If you take some time to delve into the data, you're likely to wonder what some of the values mean. Is a Tsunami Event Validity of 1 better or worse, more or less valid, or ... what than a Tsunami Event with a validity of 4? For completeness, here is a legend for select fields along with commentary:

### <u>Tsunami Event Validity (Valid values: -1 to 4)</u>
 - -1	erroneous entry
 - 0	event that only caused a seiche or disturbance in an inland river
 - 1	very doubtful tsunami
 - 2	questionable tsunami
 - 3	probable tsunami
 - 4	definite tsunami

*Scores less than 4 will be dropped. Originally, this was to be scores less than 3 however some of the other dropped fields had the only rows with probable tsunami* 

### <u>Deaths from the Tsunami and the Source Event</u>
When a description was found in the historical literature instead of an actual number of deaths, this value was coded and listed in the Deaths column. If the actual number of deaths was listed, a descriptor was also added for search purposes.
 - 0	None
 - 1	Few (~1 to 50 deaths)
 - 2	Some (~51 to 100 deaths)
 - 3	Many (~101 to 1000 deaths)
 - 4	Very many (over 1000 deaths)

### <u>Tsunami Cause Code:</u> <br>
Valid values: 0 to 11
 - 0  - 	Unknown
 - 1  - 	Earthquake
 - 2  - 	Questionable Earthquake
 - 3  - 	Earthquake and Landslide
 - 4  - 	Volcano and Earthquake
 - 5  - 	Volcano, Earthquake, and Landslide
 - 6  - 	Volcano
 - 7  - 	Volcano and Landslide
 - 8  - 	Landslide
 - 9  - 	Meteorological
 - 10 - 	Explosion
 - 11 - 	Astronomical Tide

 Oddly enough, the only codes present are 1, 3, and 4 which is strange because we tend to think of earthquakes (#1) causing them.

[Top ](#table-of-contents)
