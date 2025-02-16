# website/mood.py

from textblob import TextBlob

def analyze_mood(text):
    """
    Analyze the sentiment of the given text and extract key phrases.
    
    Returns:
      sentiment_score: A float representing the polarity (-1.0 to 1.0)
      key_phrases: A comma-separated string of noun phrases from the text
    """
    # Create a TextBlob object which automatically tokenizes the text
    blob = TextBlob(text)
    
    # Polarity is a float within the range [-1.0, 1.0] where:
    # -1.0 is very negative, 0 is neutral, and 1.0 is very positive.
    sentiment_score = blob.sentiment.polarity
    
    # Extract noun phrases, which often represent key topics or subjects in the text.
    key_phrases = ", ".join(blob.noun_phrases)
    
    return sentiment_score, key_phrases
