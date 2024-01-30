from flask import Flask, abort, request, Response
import requests
import re
import os


app = Flask(__name__)

# Get environment variables
prowlarr_url = os.environ.get('prowlarr_url')
x_api_key = os.environ.get('x_api_key')
auth_token = os.environ.get('auth_token')
proxy_url = os.environ.get('proxy_url')

real_debrid_api_url = 'https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/'

@app.route('/<int:id>/download')
def download(id):
    download_url = f"{prowlarr_url}/{id}/download"
    print(download_url)
    # Voeg query parameters toe aan de download URL
    query_string = request.query_string.decode('utf-8')
    volledige_url = f"{download_url}?{query_string}" if query_string else download_url

    # Stuur een verzoek naar de download URL en haal de response op
    response = requests.get(volledige_url, allow_redirects=False)

     # Haal de magnet link op uit de 'Location' header
    location_header = response.headers.get('Location')
    if location_header:
        # Extract de torrent hash uit de magnet link
        torrent_hash = re.search(r'btih:([a-zA-Z0-9]+)', location_header)
        if torrent_hash:
            torrent_hash = torrent_hash.group(1)
            # Check beschikbaarheid op Real-Debrid
            beschikbaarheid_url = f"{real_debrid_api_url}{torrent_hash}?auth_token={auth_token}"
            rd_response = requests.get(beschikbaarheid_url)
            print(rd_response.text)
            print(len(rd_response.text))
            if len(rd_response.text) > 60:
                return Response("Redirecting...", status=302, headers={"Location": location_header})
            else:
             abort(404)  # Geeft een 404 foutmelding terug
        else:
             abort(404)  # Geeft een 404 foutmelding terug

    return "Geen magnet link gevonden"

@app.route('/', defaults={'id': None})
@app.route('/<int:id>/', defaults={'path': ''})
@app.route('/<int:id>/<path:path>')
def mirror(id, path):
    if id is not None:
        # Voeg de id toe aan het pad
        path = f"{id}/{path}"
        basis_url = f"{prowlarr_url}/{id}/api/"
        print(basis_url)

    # Combineer de basis URL met het meegegeven pad en query parameters
    volledige_url = f"{basis_url}{path}"
    if request.query_string:
 # Gebruik alleen de querystring in de URL
        query_string = request.query_string.decode('utf-8')
        volledige_url = f"{basis_url}?{query_string}" if query_string else basis_url
        print(volledige_url)

    # Stuur een verzoek naar de oorspronkelijke API en haal de response op
    headers = {'x-api-key': x_api_key}
    response = requests.get(volledige_url, headers=headers)
    content = response.content
    if 't=tvsearch' in request.query_string.decode('utf-8'):
        # Vervang de URL in de response
        content = re.sub(
            rf"{prowlarr_url}/{id}/download",
            f"{proxy_url}/{id}/download",
            content.decode('utf-8')
        )
        content = content.encode('utf-8')

    # Stuur de aangepaste response terug naar de client
    return Response(content, status=response.status_code, content_type=response.headers['Content-Type'])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
