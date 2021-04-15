"""
@seoseb
Testproject for streamlit
Import a GSC Error Report for URLs with a bad CLS and get a table ob elements
that contribute to each URL's CLS

Script calls PSI API for each URL in upload file and extracts CLS Elements
from API Response

inspired and motivated by Charly Wargnier @DataChaz
"""

# imports

import streamlit as st
import requests
import base64
import pandas as pd

# variables

RequestURL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# request paramaeters
# Params = {"key":ApiKey, "url": singleUrlToCheck, "strategy": Device, "category": TestArt, "locale" : Sprache}

# list of URLs to check
urlsToCheck = []

# lists for collecting results
clsItems = []
lcpItems = []
imageEncodingItems = []
responsiveImagesItems = []


###
# function for calling API and extracting CLS Elements
###
def run_check(url_list):
    run = 0
    progress_max = len(url_list)

    # progress bar placeholder
    bar = st.progress(run)

    for singleUrlToCheck in url_list:
        params = {"key": ApiKey, "url": singleUrlToCheck, "strategy": device, "category": test_type, "locale": locale}
        response = requests.get(RequestURL, params)

        run = run + 1

        if response.status_code == 200:

            response_data = response.json()

            # checked URL
            check_url = response_data['id']

            # reported cls
            cls = str(response_data['lighthouseResult']['audits']['cumulative-layout-shift']['displayValue'])

            # extracting cls elements
            cls_elements = len(response_data['lighthouseResult']['audits']['layout-shift-elements']['details']['items'])

            # write cls elements and values to list 'cls_elements'
            if cls_elements > 0:
                for i in range(cls_elements):
                    clsItems.append([check_url,
                                     cls,
                                     cls_elements,
                                     response_data['lighthouseResult']['audits']['layout-shift-elements']['details']['items'][
                                         i]['score'],
                                     response_data['lighthouseResult']['audits']['layout-shift-elements']['details']['items'][
                                         i]['node']['snippet'],
                                     response_data['lighthouseResult']['audits']['layout-shift-elements']['details']['items'][
                                         i]['node']['nodeLabel'],
                                     response_data['lighthouseResult']['audits']['layout-shift-elements']['details']['items'][
                                         i]['node']['selector']
                                     ])
            else:
                clsItems.append([check_url,
                                 cls,
                                 cls_elements,
                                 "NA",
                                 "NA",
                                 "NA"
                                 ])
        else:
            st.error('Calling API for ' + singleUrlToCheck + ' failed :(')

        # update the progress bar with each iteration.
        bar.progress(run / progress_max)

    st.success('extracted %s elements' % len(clsItems))

    cls_elements_export = pd.DataFrame(clsItems, columns=["URL", "URL-cls", "cls Element Count", "Element cls Value",
                                                          "Element Node", "Node Label", "Node Selector"])

    base64_data_frame = base64.b64encode(cls_elements_export.to_csv(index=False).encode()).decode()

    st.subheader('have a quick look at the data')
    st.write(cls_elements_export)

    href = f'<a href="data:file/csv;base64,{base64_data_frame}" download="Mapping_to_URL.csv">↴ Download Table</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.markdown('_Save, inspect and fix those shifts :) _')

    return clsItems


###

# Title for Streamlit App

st.image('https://www.seoseb.de/img/seoseb_icon_x96.png')
st.title('PSI-API Extractor for CLS Elements')

st.markdown('Check which elements are shiftet during page load and how much they contribute to CLS of a given URL'
            ' by uploading a CLS Error Report from Google Search Console')

st.subheader('Enter your API key*:')

ApiKey = st.text_input('Your PSI API Key *will not be saved nor transferred elsewhere',
                       'a long string with characters and digits')
st.markdown(
    '_Need an API key? Get yours here: [developers.google.com]('
    'https://developers.google.com/speed/docs/insights/v5/get-started#APIKey)_')

st.subheader('Upload your Search Console CLS error export table')
st.image('gsc-export-screen.png', caption='This is where you find the file you need: choose Export > Download CSV')

# upload GSC export file
uploaded_file = st.file_uploader("Upload your downloaded csv file here:")

if uploaded_file is not None:

    importUrls = pd.read_csv(uploaded_file, sep=",")

    for Row in importUrls.index:
        urlsToCheck.append(importUrls["URL"][Row])

st.write('You\'re about to check ' + str(len(urlsToCheck)) + ' URLs: ')
st.write(urlsToCheck)

# set request variables

device = st.radio('select device tyoe to check pagespeed on: ', ('Mobile', 'Desktop'))
test_type = "PERFORMANCE"
locale = "de-DE"

if st.button('Check for CLS Elements'):
    run_check(urlsToCheck)
else:
    st.write('waiting for your go!')

st.markdown('---')
st.markdown('fiddled by [seoseb](https://www.seoseb.de/) | [@seoseb](https://twitter.com/seoseb)')
