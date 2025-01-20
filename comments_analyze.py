import aiohttp
import asyncio
import numpy as np
from collections import Counter
from openai import AsyncOpenAI
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import cdist
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

YOUTUBE_API_KEY = "AIzaSyAjsyZtdDt9-yP3x2W5tHiQqEqet1ip3Y4"
OPENAI_API_KEY = "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"
VIDEO_ID = "b--nRgmCvrY"
SEMAPHORE_LIMIT = 10
MAX_RETRIES = 3

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
SEMAPHORE = asyncio.Semaphore(SEMAPHORE_LIMIT)


async def fetch_page(session, video_id, page_token=None):
    """
    Fetches a page of comments from the YouTube API.

    :param session: aiohttp.ClientSession - Active client session for making requests.
    :param video_id: str - The ID of the video to fetch comments for.
    :param page_token: str, optional - Token for the next page of results.
    :return: dict - JSON response containing comment data.
    :raises Exception: If the API response status is not 200.
    """
    logging.debug("Fetching comments page.")
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": 100,
        "key": YOUTUBE_API_KEY,
    }
    if page_token:
        params["pageToken"] = page_token

    async with session.get(url, params=params) as response:
        if response.status != 200:
            logging.error(f"YouTube API error: {response.status} - {await response.text()}")
            raise Exception(f"YouTube API error: {response.status}")
        logging.info("Successfully fetched a page of comments.")
        return await response.json()


async def get_youtube_comments(video_id, max_comments=32768):
    """
    Retrieves comments for a specific YouTube video.

    :param video_id: str - The ID of the video to fetch comments for.
    :param max_comments: int - Maximum number of comments to retrieve.
    :return: list - A list of comments.
    """
    logging.debug(f"Starting to fetch comments for video ID: {video_id}")
    comments = []
    next_page_token = None

    async with aiohttp.ClientSession() as session:
        with tqdm(total=max_comments, desc="Fetching comments") as pbar:
            while len(comments) < max_comments:
                try:
                    response = await fetch_page(session, video_id, next_page_token)
                except Exception as e:
                    logging.critical(f"Critical error fetching page: {e}")
                    break

                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
                    if len(comment) > 128:
                        logging.debug(f"Skipping long comment: {comment}")
                        continue
                    comments.append(comment)
                    pbar.update(1)

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    logging.info("No more pages to fetch.")
                    break

    logging.info(f"Total comments fetched: {len(comments)}")
    return comments[:max_comments]


async def fetch_embedding(comment):
    """
    Fetches the embedding for a given comment.

    :param comment: str - The comment text to generate the embedding for.
    :return: np.ndarray - Normalized embedding vector.
    :raises Exception: If unable to fetch embedding after retries.
    """
    logging.debug(f"Fetching embedding for comment: {comment}")

    def normalize_l2(x):
        x = np.array(x)
        if x.ndim == 1:
            norm = np.linalg.norm(x)
            if norm == 0:
                return x
            return x / norm
        else:
            norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
            return np.where(norm == 0, x, x / norm)

    for attempt in range(MAX_RETRIES):
        try:
            async with SEMAPHORE:
                response = await client.embeddings.create(
                    input=comment,
                    model="text-embedding-3-small",
                    encoding_format="float"
                )
                cut_dim = response.data[0].embedding[:256]
                logging.info("Successfully fetched embedding.")
                return normalize_l2(cut_dim)
        except Exception as e:
            logging.warning(f"Error fetching embedding (Attempt {attempt + 1}): {e}")
            await asyncio.sleep(2 ** attempt)
    logging.error("Failed to fetch embedding after multiple attempts.")
    raise Exception("Failed to fetch embedding.")


async def get_embeddings(comments):
    """
    Fetches embeddings for a list of comments.

    :param comments: list - List of comments.
    :return: np.ndarray - Array of embedding vectors.
    """
    logging.debug(f"Fetching embeddings for {len(comments)} comments.")
    embeddings = []
    successful = 0

    async def fetch_with_timeout(comment, timeout=100):
        try:
            return await asyncio.wait_for(fetch_embedding(comment), timeout=timeout)
        except asyncio.TimeoutError:
            logging.warning(f"Timeout fetching embedding for comment: {comment}")
        except Exception as e:
            logging.error(f"Error fetching embedding for comment: {e}")
        return None

    tasks = [fetch_with_timeout(comment) for comment in comments]

    for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching embeddings"):
        result = await task
        if result is not None:
            embeddings.append(result)
            successful += 1

    logging.info(f"Successfully fetched {successful} embeddings out of {len(comments)} comments.")
    return np.array(embeddings)


def cluster_embeddings_with_progress(embeddings, n_clusters=10, method="kmeans", eps=0.5, min_samples=5,
                                     linkage="ward"):
    """
    Clusters embeddings using the specified clustering method.

    :param embeddings: np.ndarray - Array of embedding vectors.
    :param n_clusters: int - Number of clusters to create.
    :param method: str - Clustering method ('kmeans' or 'hierarchical').
    :param eps: float, optional - DBSCAN epsilon parameter.
    :param min_samples: int, optional - Minimum samples for DBSCAN.
    :param linkage: str - Linkage type for hierarchical clustering.
    :return: np.ndarray - Cluster labels for each embedding.
    """
    logging.debug(f"Starting clustering with method: {method}")
    if method == "kmeans":
        logging.info("Using KMeans clustering.")
        kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
        labels = kmeans.fit_predict(embeddings)
        logging.info("Clustering complete.")
    elif method == "hierarchical":
        logging.info("Using Agglomerative (Hierarchical) clustering.")
        hierarchical_clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
        labels = hierarchical_clustering.fit_predict(embeddings)
        logging.info(f"Found {n_clusters} clusters.")
    else:
        logging.error("Invalid clustering method provided.")
        raise ValueError("Clustering method must be 'kmeans' or 'hierarchical'.")

    return labels


async def extract_keywords(comments, embeddings, labels, n_center=10):
    """
    Extracts key phrases for each cluster using embeddings and comments.

    :param comments: list - List of comments to process.
    :param embeddings: np.ndarray - Array of embedding vectors for the comments.
    :param labels: np.ndarray - Cluster labels for the comments.
    :param n_center: int - Number of center points to use for summarization.
    :return: dict - A dictionary of cluster summaries and keywords.
    """
    logging.info("Starting keyword extraction for clusters.")
    cluster_comments = {cluster_id: [] for cluster_id in set(labels) if cluster_id != -1}
    cluster_embeddings = {cluster_id: [] for cluster_id in set(labels) if cluster_id != -1}

    for comment, embedding, label in zip(comments, embeddings, labels):
        if label != -1:
            cluster_comments[label].append(comment)
            cluster_embeddings[label].append(embedding)

    cluster_keywords = {}

    for cluster_id in tqdm(cluster_comments.keys(), desc="Processing clusters"):
        try:
            cluster_embeds = np.array(cluster_embeddings[cluster_id])
            cluster_center = np.mean(cluster_embeds, axis=0)

            distances = cdist([cluster_center], cluster_embeds, metric="euclidean")[0]
            center_indices = distances.argsort()[:n_center]
            center_comments = [cluster_comments[cluster_id][i] for i in center_indices]

            # Summarization prompt
            summary_prompt = (
                "Act as an assistant. Summarize the following text data using RU language. "
                "Provide a concise and relevant summary in less than 10 words.\n\n"
                f"Text: {' '.join(center_comments)}"
            )
            summary_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": summary_prompt}],
                max_tokens=100,
            )
            summary = summary_response.choices[0].message.content.strip()

            # Keywords prompt
            keywords_prompt = (
                "Extract 5 most relevant keywords from the following text data "
                "in its original language. Return them as a comma-separated list.\n\n"
                f"Text: {summary}"
            )
            keywords_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": keywords_prompt}],
                max_tokens=50,
            )
            keywords = keywords_response.choices[0].message.content.strip().split(",")

            cluster_keywords[cluster_id] = {
                "summary": summary,
                "keywords": [kw.strip() for kw in keywords]
            }
            logging.debug(f"Cluster {cluster_id} keywords: {cluster_keywords[cluster_id]['keywords']}")
        except Exception as e:
            logging.error(f"Error processing cluster {cluster_id}: {e}")

    logging.info("Keyword extraction completed.")
    return cluster_keywords


def generate_wordcloud(cluster_keywords):
    """
    Generates and displays a word cloud based on extracted keywords.

    :param cluster_keywords: dict - A dictionary containing keywords for each cluster.
    """
    logging.info("Generating word cloud from cluster keywords.")
    all_keywords = []
    for data in cluster_keywords.values():
        all_keywords.extend(data["keywords"])

    word_counts = Counter(all_keywords)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    logging.info("Word cloud generated successfully.")


