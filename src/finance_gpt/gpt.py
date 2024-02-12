from finance_gpt.utils import load_credentials
from finance_gpt.news_api import NewsArticle, GPTSentiment
from finance_gpt.utils import setup_logger
from openai import OpenAI

logger = setup_logger(__name__)

class GPT():
    
    def __init__(self, model_name: str = "gpt-4-1106-preview"):
        self._load_api_key()
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key)
        
    def _load_api_key(self):
        """Loads the API key from the credentials file."""
        try:
            creds = load_credentials()
        except:
            raise Exception("Not able to load in credentials, please make sure you have a credentials file with the correct format.")
        
        self.api_key = creds["chat_gpt"]["key"]
        
    def get_prompt(self,  news_article: NewsArticle, term: str) -> str:
        
        prompt = 'Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer “YES” if good news, “NO” if bad news, or “UNKNOWN” if uncertain in the first line. Then elaborate with one short and concise sentence on the next line. '
        prompt += f"Is this headline good or bad for the stock price of {news_article.company.value} in the {term} term?"
        
        prompt += f"Headline: {news_article.title}"

        return prompt
        
    def get_sentiment(self, news_article: NewsArticle, term: str):
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            seed=1,
            temperature=0.5,
            messages=[{"role": "user", "content": self.get_prompt(news_article, term)}]
        )
        
        logger.debug(f"This is the response: {response.choices[0].message.content}")
        
        splits = response.choices[0].message.content.split("\n")
        
        logger.debug(f"The splits: {splits}")
        
        filtered_splits = []
        for split in splits:
            if len(split) > 0:
                filtered_splits.append(split)
        logger.debug(f"The filtered splits: {splits}")
        
        # check if sentiment is correct
        sentiment = filtered_splits[0]
        if sentiment.lower() not in ["no", "yes", "unknown"]:
            logger.warn(f"Sentiment is weird: {sentiment}")
            
            if "no" in sentiment:
                sentiment = "NO"
                logger.debug("Using sentiment NO")
            elif "yes" in sentiment:
                sentiment = "YES"
                logger.debug("Using sentiment YES")
            else:
                raise Exception("Dont know what to do with this sentiment")
            
        
        sentiment, reasoning = filtered_splits
        
        logger.debug(f"The sentiment: {sentiment}")
        logger.debug(f"The reasoning: {reasoning}")
        
        sentiment = GPTSentiment[sentiment]

        news_article.gpt_sentiment = sentiment
        news_article.gpt_verdict = reasoning
    

        
if __name__ == "__main__":
    from finance_gpt.news_api import NewsApi
    
    gpt = GPT()
    
    news_api = NewsApi()
    news = news_api.get_news("AMZN")
    
    print(gpt.get_sentiment(news_article=news[0], term="short"))