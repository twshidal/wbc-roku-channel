import feedparser
import json
import re
from datetime import datetime, timezone

# Constant variables
RSS_URL = "https://worthbc.sermon.net/rss/tv/video"
DIRECTOR = 'Worth Baptist Church'
ADS = 'False'
ARTIST = 'Worth Baptist Church'
GENRES = 'Religion, Christianity'
RATING = 'NR'
QUALITY = 'HD'
VIDEO_TYPE = "mp4"
JSON_FILE = "docs/WorthBC.json"
DEFAULT_POSTER_URL = "https://media.worthbc.org/images/media/roku/channel-poster_hd_290x218px.png"

def parse_duration(duration_string):
    try:
        parts = duration_string.strip().split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:
            return int(parts[0])
    except (ValueError, TypeError):
        pass
    return 0

def extract_custom_series_from_tags(tags):
    if not tags:
        return None
    for tag in tags:
        term = tag.get('term', '')
        # Look for "WBC-TV:" and capture the value after it
        if 'WBC-TV:' in term:
            match = re.search(r'WBC-TV:\s*([^,]+)', term)
            if match:
                return match.group(1).strip()
    return None


def main():
    feed = feedparser.parse(RSS_URL)

    # Extract channel info
    channel = feed.feed
    json_header = {
        "title": channel.get('title', 'N/A'),
        "link": channel.get('link', 'N/A'),
        "description": channel.get('description', 'N/A'),
    }

    json_data = []

    for entry in feed.entries:
        if (entry.title != 'Live broadcast for Worth Baptist Church' and
                not entry.title.startswith('Live broadcast for Worth Baptist Church - ') and
                'for Worth Baptist Church' not in entry.get('description', '')):

            episode = entry.link.split('.net/')[-1]
            summary = entry.get('summary', '').split('\n\n')
            description = summary[0] if summary else 'N/A'

            speaker_name = "Unknown Speaker"
            service_event = "Service"
            service_date = "1970/01/01"
            try:
                description_split = description.split(', ')
                speaker_name = description_split[0]
                service_event = description_split[-2]
                service_date = description_split[-1]
            except (IndexError, ValueError):
                pass

            short_description = f"{service_event}, {service_date}"

            try:
                service_date_split = service_date.split('/')
                service_year = service_date_split[2]
                service_month = service_date_split[0].zfill(2)
                service_day = service_date_split[1].zfill(2)
                release_date = f"{service_year}-{service_month}-{service_day}"
            except (IndexError, ValueError):
                release_date = "1970-01-01"

            date_added = f"{release_date}T00:00:00Z"

            duration_str = entry.get('itunes_duration', '0')
            duration = parse_duration(duration_str)

            poster_url = (entry.get('image', {}).get('href') or DEFAULT_POSTER_URL)

            # Extract WBC-TV custom series value
            custom_series = extract_custom_series_from_tags(entry.get('tags', []))

            feed_item = {
                'id': str(episode),
                'title': entry.title,
                'description': description,
                'cast': [speaker_name] if speaker_name else [],
                'rating': RATING,
                'director': DIRECTOR,
                'shortDescription': short_description,
                'longDescription': speaker_name,
                'releaseDate': release_date,
                'genres': GENRES.split(', '),
                'thumbnail': poster_url,
                'tags': [speaker_name, service_event, service_date],
                'customSeries': custom_series,
                'content': {
                    'dateAdded': date_added,
                    'duration': duration,
                    'videos': [
                        {
                            'url': entry.get('guid', entry.link),
                            'quality': QUALITY,
                            'videoType': VIDEO_TYPE
                        }
                    ]
                }
            }

            json_data.append(feed_item)

    json_data.sort(key=lambda x: x['releaseDate'], reverse=True)

    output_data = {
        "providerName": DIRECTOR,
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "language": "en",
        "channel_info": json_header,
        "movies": json_data
    }

    with open(JSON_FILE, 'w') as local_json_file:
        json.dump(output_data, local_json_file, indent=4)

if __name__ == "__main__":
    main()
