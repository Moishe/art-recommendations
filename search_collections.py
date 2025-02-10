import json
import os
import os
import requests
from typing import Optional, Dict, List
import logging

class MuseumImageFinder:
    def __init__(self, smithsonian_api_key: str, logging_level: int = logging.INFO):
        """
        Initialize the museum image finder with necessary API keys.

        Args:
            smithsonian_api_key: API key for Smithsonian API
            logging_level: Optional logging level (default: logging.INFO)
        """
        self.smithsonian_api_key = os.getenv("SMITHSONIAN_API_KEY", smithsonian_api_key)
        # Met doesn't require an API key

        # Setup logging
        logging.basicConfig(level=logging_level)
        self.logger = logging.getLogger(__name__)

    def find_artwork_image(self, artist_name: str, artwork_title: Optional[str] = None) -> Dict:
        """
        Search for an artwork across multiple museum APIs and return the first matching image URL.

        Args:
            artist_name: Name of the artist
            artwork_title: Optional specific artwork title to search for

        Returns:
            Dict containing:
                - success: boolean indicating if an image was found
                - url: image URL if found, None if not
                - source: source museum if found
                - title: artwork title if found
                - rights: rights information if available
        """
        self.logger.info(f"Searching for artwork by {artist_name}")

        # Try Met API first
        """
        met_result = self._search_met(artist_name, artwork_title)
        if met_result['success']:
            return met_result
        """
        # Try Smithsonian API next
        smith_result = self._search_smithsonian(artist_name, artwork_title)
        if smith_result['success']:
            return smith_result

        return {
            'success': False,
            'url': None,
            'source': None,
            'title': None,
            'rights': None,
            'error': 'No matching artwork found in any museum API'
        }

    def _search_met(self, artist_name: str, artwork_title: Optional[str] = None) -> Dict:
        """Search the Metropolitan Museum of Art's API"""
        self.logger.info("Searching Met API...")

        base_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
        query = f"artistOrCulture=true&q={artist_name}"

        try:
            # Get object IDs matching the artist
            response = requests.get(base_url + "?" + query)
            response.raise_for_status()
            data = response.json()

            if data['total'] == 0:
                return {'success': False, 'error': 'No matches found in Met collection'}

            # Get details for each object
            for object_id in data['objectIDs'][:5]:  # Limit to first 5 to avoid too many requests
                object_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
                obj_response = requests.get(object_url)
                obj_response.raise_for_status()
                obj_data = obj_response.json()

                # Check if this object has an image and matches title if provided
                if obj_data.get('primaryImage') and (
                    not artwork_title or
                    artwork_title.lower() in obj_data['title'].lower()
                ):
                    return {
                        'success': True,
                        'url': obj_data['primaryImage'],
                        'source': 'Metropolitan Museum of Art',
                        'title': obj_data['title'],
                        'rights': obj_data.get('rights'),
                        'object_url': f"https://www.metmuseum.org/art/collection/search/{object_id}"
                    }

            return {'success': False, 'error': 'No suitable image found in Met collection'}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error querying Met API: {str(e)}")
            return {'success': False, 'error': f"Met API error: {str(e)}"}

    def _search_smithsonian(self, artist_name: str, artwork_title: Optional[str] = None) -> Dict:
        """Search the Smithsonian API"""
        self.logger.info("Searching Smithsonian API...")

        base_url = "https://api.si.edu/openaccess/api/v1.0/search"

        # Construct query
        query = f"q={artist_name}"
        if artwork_title:
            query += f"+AND+title:\"{artwork_title}\""

        headers = {
            'api_key': self.smithsonian_api_key
        }

        try:
            response = requests.get(f"{base_url}?{query}&rows=1000&api_key={self.smithsonian_api_key}", headers=headers)
            response.raise_for_status()
            data = response.json()

            for row in data.get('response', {}).get('rows', []):
                content = row.get('content', {})

                # Check for matching images
                print(content['descriptiveNonRepeating']['title']['content'])
                print(json.dumps(content.get('descriptiveNonRepeating', {}).get('online_media', {}), indent=2))

                if content.get('descriptiveNonRepeating', {}).get('online_media', {}).get('media', []):
                    media = content['descriptiveNonRepeating']['online_media']['media'][0]
                    if media.get('content', {}):
                        return {
                            'success': True,
                            'url': media.get('content', {}),
                            'source': 'Smithsonian',
                            'title': content.get('descriptiveNonRepeating', {}).get('title', {}).get('content'),
                            'rights': content.get('freetext', {}).get('rights', [{}])[0].get('content'),
                            'object_url': content.get('descriptiveNonRepeating', {}).get('record_link')
                        }

                    if media.get('resources', []):
                        image_url = media['resources'][0].get('url')
                        if image_url:
                            return {
                                'success': True,
                                'url': image_url,
                                'source': 'Smithsonian',
                                'title': content.get('descriptiveNonRepeating', {}).get('title', {}).get('content'),
                                'rights': content.get('freetext', {}).get('rights', [{}])[0].get('content'),
                                'object_url': content.get('descriptiveNonRepeating', {}).get('record_link')
                            }

            return {'success': False, 'error': 'No suitable image found in Smithsonian collection'}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error querying Smithsonian API: {str(e)}")
            return {'success': False, 'error': f"Smithsonian API error: {str(e)}"}

if __name__=="__main__":
    finder = MuseumImageFinder(smithsonian_api_key=os.getenv("SMITHSONIAN_API_KEY", "none"))
    res = finder.find_artwork_image("Imogen Cunningham")
    print(res)
