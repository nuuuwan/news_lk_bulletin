import sys

from news_lk_bulletin import NewsBulletin
from utils_future import LLM


def main():
    openai_api_key = sys.argv[1]
    llm = LLM(openai_api_key)
    NewsBulletin(llm=llm, max_articles=100, max_data_bytes=35_000).write()


if __name__ == "__main__":
    main()
