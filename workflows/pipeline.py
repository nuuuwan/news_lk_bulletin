import sys

from utils import Log

from news_lk_bulletin import NewsBulletin
from utils_future import LLMMistralAI, LLMOpenAI

log = Log('pipeline')


def main():
    llm_name = sys.argv[1]
    api_key = sys.argv[2]

    for LLM in [LLMOpenAI, LLMMistralAI]:
        if LLM.NAME == llm_name:
            break
    log.info(f'Using {LLM.NAME}...')
    llm = LLM(api_key)
    NewsBulletin(llm=llm).write()


if __name__ == "__main__":
    main()
