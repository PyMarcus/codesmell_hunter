from app.service.base_links_code_download import BaseLinksCodeDownload


QUESTION: str = """I need to check if the Java code below contains code smells (aka bad smells). Could you please
identify which smells occur in the following code? However, do not describe the smells, just list them.
Please start your answer with "YES I found bad smells" when you find any bad smell. Otherwise, start your answer with
"NO, I did not find any bad smell".
When you start to list the detected bad smells, always put in your answer "the bad smells are:" amongst the text your
answer and always separate it in this format: 1.Long method, 2.Feature envy """


if __name__ == '__main__':
    gpt = BaseLinksCodeDownload(QUESTION)
    gpt.start()
