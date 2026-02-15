import logging
import os
import re
import requests

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "goldstar611"
}


def get_links_from_url(url, headers):
    # Fetch the webpage
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract all links
    links = soup.find_all("a")

    return links


def download_file(url, headers, save_path):
    try:
        logger.info(f"Downloading: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(response.content)

        logger.debug(f"Downloaded: {url} to {save_path}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading the file: {e}")
    except Exception as e:
        logger.error(f"Error saving the file: {e}")


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        chirp_links = {}

        url = "https://archive.chirpmyradio.com/chirp_next/"
        links = get_links_from_url(url, headers)
        logger.debug(f"Found {len(links)} links on {url}")
        
        for link in links:
            href = link.get("href")
            text = link.get_text(strip=True)

            if href and re.match(r"^next-\d+/$", text):
                logger.info(f"Found CHIRP release link: {href}")
                chirp_links[href] = {"downloads": "", "checksums": ""}
            else:
                logger.debug(f"Skipping non-CHIRP release link: {href} with text: {text}")

        for chirp_release_link in chirp_links:
            logger.debug(f"Processing release link: {chirp_release_link}")
            url = f"https://archive.chirpmyradio.com/chirp_next/{chirp_release_link}"
            links = get_links_from_url(url, headers)
            logger.debug(f"Found {len(links)} links on {url}")

            for link in links:
                href = link.get("href")
                text = link.get_text(strip=True)
                #Looking for `chirp-20260206-py3-none-any.whl`
                if href and re.match(r"^chirp-.*\.whl$", text):
                    logger.info(f"Found download link: {href}")
                    chirp_links[chirp_release_link]["downloads"] = f"{url}{href}"
                    #https://archive.chirpmyradio.com/chirp_next/next-20260206/SHA1SUM
                    chirp_links[chirp_release_link]["checksums"] = f"{url}SHA1SUM"
                else:
                    logger.debug(f"Skipping non-wheel download link: {href} with text: {text}")

        logger.info("CHIRP Download Links:")
        for release_link, links_data in chirp_links.items():
            logger.info(f"Release: {release_link}")
            logger.info(f"  Download: {links_data['downloads']}")
            logger.info(f"  Checksum: {links_data['checksums']}")

            wheel_name = os.path.basename(links_data["downloads"])
            sha1sum_name = os.path.basename(links_data["checksums"])

            # download the wheel file and checksum file
            if links_data["downloads"]:
                if not os.path.exists(f"downloads/{release_link}{wheel_name}"):
                    download_file(links_data["downloads"], headers, f"downloads/{release_link}{wheel_name}")
                else:
                    logger.info(f"Wheel file already exists for {release_link}, skipping download.")

            if links_data["checksums"]:
                if not os.path.exists(f"downloads/{release_link}{sha1sum_name}"):
                    download_file(links_data["checksums"], headers, f"downloads/{release_link}{sha1sum_name}")
                else:
                    logger.info(f"Checksum file already exists for {release_link}, skipping download.")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the URL: {e}")
    except Exception as e:
        logger.error(f"Error parsing the page: {e}")


if __name__ == "__main__":
    main()
