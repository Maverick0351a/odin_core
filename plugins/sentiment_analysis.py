"""
Sentiment Analysis Plugin for ODIN Protocol
Analyzes message sentiment and adds metadata.
"""

from odin_sdk.plugins import BasePlugin
from typing import Dict, Any
import re


class SentimentAnalysisPlugin(BasePlugin):
    """Plugin that analyzes message sentiment."""
    
    @property
    def name(self) -> str:
        return "sentiment-analysis"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Analyzes message sentiment and emotional tone"
    
    async def initialize(self) -> bool:
        """Initialize sentiment analysis."""
        self.logger.info("Initializing sentiment analysis plugin")
        
        # Simple sentiment word lists (in production, use proper NLP)
        self.positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied'
        ]
        
        self.negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'angry', 'frustrated', 'disappointed', 'sad', 'upset'
        ]
        
        return True
    
    async def process_message(self, message: Any, context: Dict[str, Any]) -> Any:
        """Analyze message sentiment."""
        if not hasattr(message, 'raw_output'):
            return message
        
        content = message.raw_output.lower()
        
        # Count sentiment words
        positive_count = sum(1 for word in self.positive_words if word in content)
        negative_count = sum(1 for word in self.negative_words if word in content)
        
        # Calculate sentiment score (-1 to 1)
        total_words = len(content.split())
        if total_words == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        
        # Determine sentiment category
        if sentiment_score > 0.1:
            sentiment = "positive"
        elif sentiment_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Add sentiment to message metadata
        if hasattr(message, 'metadata'):
            message.metadata["sentiment"] = sentiment
            message.metadata["sentiment_score"] = str(sentiment_score)
            message.metadata["positive_words"] = str(positive_count)
            message.metadata["negative_words"] = str(negative_count)
        
        self.logger.info(f"Sentiment analysis: {sentiment} (score: {sentiment_score:.3f})")
        
        return message
