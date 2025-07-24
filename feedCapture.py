import feedparser
import json
import re
import os
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
OUTPUT_FOLDER = "docs"
JSON_FILE = os.path.join(OUTPUT_FOLDER, "WorthBC.json")
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

def extract_keyword_values(entry):
    """Extract customSeries and playStart from tags."""
    custom_series = None
    play_start = None

    try:
        keywords = [tag['term'] for tag in entry.get('tags', []) if 'term' in tag]
        for kw in keywords:
            if 'WBC-TV:' in kw:
                custom_series = kw.split('WBC-TV:')[1].strip()
            if 'PlayStart:' in kw:
                play_start = kw.split('PlayStart:')[1].strip()
    except Exception:
        pass

    return custom_series, play_start

def sanitize_filename(name):
    return re.sub(r'[^\w\-]', '_', name)

def build_output_json(header, movies):
    return {
        "providerName": DIRECTOR,
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "language": "en",
        "channel_info": header,
        "movies": movies
    }

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
    series_dict = {}

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

            # Extract custom values
            custom_series, playStart_str = extract_keyword_values(entry)
            playStart = parse_duration(str(playStart_str)) if playStart_str else 0

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
                    'playStart': playStart,
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

            # Group by series if available
            if custom_series:
                if custom_series not in series_dict:
                    series_dict[custom_series] = []
                series_dict[custom_series].append(feed_item)

    # Sort main data
    json_data.sort(key=lambda x: x['releaseDate'], reverse=True)

    # Save main JSON
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    with open(JSON_FILE, 'w') as f:
        json.dump(build_output_json(json_header, json_data), f, indent=4)

    # Save individual series JSONs
    for series, items in series_dict.items():
        safe_name = sanitize_filename(series)
        file_path = os.path.join(OUTPUT_FOLDER, f"WorthBC_{safe_name}.json")
        with open(file_path, 'w') as f:
            json.dump(build_output_json(json_header, items), f, indent=4)

if __name__ == "__main__":
    main()
