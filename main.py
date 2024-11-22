import os
import tweepy
import anthropic
from datetime import datetime
import time
import logging
import requests
from ghost import GhostClient
import schedule

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BloopBot:
    def __init__(self):
        logging.info("Initializing Bloop...")
        
        # Initialize Twitter
        self.twitter = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        
        # Initialize Anthropic/Claude
        self.anthropic = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Initialize Ghost
        self.ghost = GhostClient(
            host=os.getenv('GHOST_HOST'),
            api_key=os.getenv('GHOST_ADMIN_API_KEY')
        )

    def generate_blog_content(self, topic):
        """Generate blog content using Claude"""
        try:
            prompt = f"""Create an engaging blog post about {topic}. 
            Include:
            - Engaging title
            - Introduction
            - Key points and analysis
            - Conclusion
            Make it informative yet conversational."""
            
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content
        except Exception as e:
            logging.error(f"Error generating content: {str(e)}")
            return None

    def publish_to_ghost(self, title, content):
        """Publish content to Ghost blog"""
        try:
            post = self.ghost.posts.create({
                'title': title,
                'content': content,
                'status': 'published'
            })
            logging.info(f"Published blog post: {title}")
            return post
        except Exception as e:
            logging.error(f"Error publishing to Ghost: {str(e)}")
            return None

    def post_tweet(self, text):
        """Post a tweet"""
        try:
            result = self.twitter.create_tweet(text=text)
            logging.info(f"Posted tweet: {text}")
            return result
        except Exception as e:
            logging.error(f"Error posting tweet: {str(e)}")
            return None

    def run_content_cycle(self):
        """Run one complete content generation and publishing cycle"""
        try:
            # Example topics (we'll make this more sophisticated later)
            topics = [
                "AI and Machine Learning Trends",
                "Future of Technology",
                "Digital Innovation",
                "Tech Industry Analysis",
                "Emerging Technologies"
            ]
            
            # Generate and publish content
            topic = topics[datetime.now().day % len(topics)]
            content = self.generate_blog_content(topic)
            
            if content:
                # Post to Ghost
                post = self.publish_to_ghost(f"Bloop's Analysis: {topic}", content)
                
                if post:
                    # Post tweet about new blog post
                    tweet_text = f"🤖 Just published my thoughts on {topic}! Check it out: {post['url']}"
                    self.post_tweet(tweet_text)
        
        except Exception as e:
            logging.error(f"Error in content cycle: {str(e)}")

def main():
    logging.info("Starting Bloop Bot...")
    bot = BloopBot()
    
    # Schedule daily content
    schedule.every().day.at("10:00").do(bot.run_content_cycle)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            time.sleep(300)

if __name__ == "__main__":
    main()
