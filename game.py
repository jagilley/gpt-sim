import langchain
from langchain.llms import OpenAI
from unstructured.partition.html import partition_html
from langchain import PromptTemplate

with open('/Users/jasper/oai.txt', 'r') as f:
    key = f.read()

llm = OpenAI(temperature=0.7, openai_api_key=key)

class game:
    def __init__(self, country_name, save_path=None):
        self.country = country_name
        # self.wikipedia = self.load_wikipedia()
        self.year = 2023
        if save_path is not None:
            with open(save_path, 'r') as f:
                self.state = f.read()
            self.save_path = save_path
        else:
            self.state = self.get_starting_state()
            self.save_path = f'saves/{self.country.lower()}-{self.year}.txt'

    def load_wikipedia(self):
        wikipedia_path = f'data/{self.country.capitalize()} - Wikipedia.html'
        with open(wikipedia_path, 'r') as f:
            html = f.read()
        return partition_html(html)
    
    def get_starting_state(self):
        return llm(f"Write a factual paragraph summarizing the current state of {self.country} in the year {self.year}.").strip()

    def get_prompt(self):
        with open('prompt_template.txt', 'r') as f:
            prompt_template = f.read()
        template = PromptTemplate(
            input_variables=["year", "country", "state_of_the_country"],
            template=prompt_template
        )
        return template.format(
            year=self.year,
            country=self.country,
            state_of_the_country=self.state,
        )
    
    def save(self, save_path):
        with open(save_path, 'w') as f:
            f.write(self.state)
    
    def play(self):
        while True:
            prompt = self.get_prompt()
            print()
            action = input(prompt)
            if action == 'q':
                break
            # self.state = llm(prompt)
            self.save(self.save_path)
            self.year += 1

if __name__ == '__main__':
    game('Afghanistan').play()