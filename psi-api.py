"""
@seoseb
first  project with streamlit
Import a GSC Error Report for URLs with a bad CLS and get a table of elements
that contribute to each URL's CLS

Script calls PSI API for each URL in uploaded file and retrieves CLS Elements
from API Response, puts them into a dataframe which can be downloaded at the end.

inspired and motivated by Charly Wargnier @DataChaz
"""

###########
# imports #
###########


import streamlit as st
import requests
import base64
import pandas as pd


#############
# variables #
#############


request_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
urls_to_check = []
cls_items = []


########################################################
# function for calling API and extracting CLS Elements #
########################################################


def run_check(url_list):
    run = 0
    progress_max = len(url_list)

    # progress bar placeholder
    bar = st.progress(run)

    for single_url_to_check in url_list:
        params = {'key': psi_api_key, 'url': single_url_to_check, 'strategy': device, 'category': test_type,
                  'locale': locale}
        response = requests.get(request_url, params)

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
                    cls_items.append([check_url,
                                      cls,
                                      cls_elements,
                                      response_data['lighthouseResult']['audits']['layout-shift-elements']['details']
                                      ['items'][i]['score'],
                                      response_data['lighthouseResult']['audits']['layout-shift-elements']['details']
                                      ['items'][i]['node']['snippet'],
                                      response_data['lighthouseResult']['audits']['layout-shift-elements']['details']
                                      ['items'][i]['node']['nodeLabel'],
                                      response_data['lighthouseResult']['audits']['layout-shift-elements']['details']
                                      ['items'][i]['node']['selector']
                                      ])
            else:
                cls_items.append([check_url,
                                  cls,
                                  cls_elements,
                                  'NA',
                                  'NA',
                                  'NA'
                                  ])
        else:
            # todo: add handler for missing API key exception
            st.error('Calling API for ' + single_url_to_check + ' failed :(')

        # update the progress bar with each iteration.
        bar.progress(run / progress_max)

    st.success('extracted %s elements' % len(cls_items))

    cls_elements_export = pd.DataFrame(cls_items, columns=['URL', 'URL-cls', 'cls Element Count', 'Element cls Value',
                                                           'Element Node', 'Node Label', 'Node Selector'])

    base64_data_frame = base64.b64encode(cls_elements_export.to_csv(index=False).encode()).decode()

    st.subheader('3. Have a quick look at the data')
    st.write(cls_elements_export)

    st.subheader('4. Export table')
    href = f'<a href="data:file/csv;base64,{base64_data_frame}" download="Mapping_to_URL.csv">↴ Download Table</a>'
    st.markdown(href, unsafe_allow_html=True)
    st.markdown('_Save, inspect and fix those shifts :) _')

    return cls_items


###########################
# Title for Streamlit App #
###########################


st.title('![@seoseb](https://www.seoseb.de/img/seoseb_icon_x48.png) PSI-API Extractor for CLS Elements')
st.markdown('Check which elements are shifted during page load and how much they contribute to CLS of a given URL'
            ' by uploading a CLS Error Report from Google Search Console.')

st.info('You\'ll need an PSI API key: '
        '[Get yours here.](https://developers.google.com/speed/docs/insights/v5/get-started#key)')

with st.beta_expander('This is where you find your export files in Google Search Console'):
    st.markdown('Go to Core Web Vitals Report in Google Search Console. '
                'Chose the device type you\'re interested in and then go to \"CLS Issues\".')
    st.image('gsc-export-screen.png', caption='To download the report data choose: Export > Download CSV')

st.markdown('---')

st.subheader('1. Setup')

# Form element collecting all the necessary configurations
with st.form(key='my_form'):
    psi_api_key = st.text_input('Your PSI API Key will not be saved nor transferred elsewhere', 'API-KEY')
    device = st.radio('select device type to check pagespeed on: ', ('Mobile', 'Desktop'))
    # upload GSC export file
    uploaded_file = st.file_uploader('Upload your downloaded csv file here:')
    submit_button = st.form_submit_button(label='Submit')

if uploaded_file is not None:

    importUrls = pd.read_csv(uploaded_file, sep=',')

    for Row in importUrls.index:
        urls_to_check.append(importUrls['URL'][Row])

    st.write('You\'re about to check ' + str(len(urls_to_check)) + ' URLs: ')
    st.write(urls_to_check)

    # set request variables

    test_type = 'PERFORMANCE'
    locale = 'de-DE'

    st.subheader('2. Fetch CLS elements')

    if st.button('▶️ Check for CLS Elements'):
        run_check(urls_to_check)
    else:
        st.write('waiting for your go!')


##########
# footer #
##########

st.markdown('---')
st.markdown('_fiddled by [seoseb](https://www.seoseb.de/) | [@seoseb](https://twitter.com/seoseb)_')
