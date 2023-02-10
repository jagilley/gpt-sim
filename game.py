import langchain
from langchain.llms import OpenAI
from unstructured.partition.html import partition_html
from langchain import PromptTemplate
import json

with open('/Users/jasper/oai.txt', 'r') as f:
    key = f.read()

llm = OpenAI(temperature=0.5, openai_api_key=key)

class policy:
    def __init__(self, action, enact_year, enact_week):
        self.action = action
        self.enact_year = enact_year
        self.enact_week = enact_week
        # self.enactment_duration = get_enactment_duration(action)

    def get_enactment_duration(self, action):
        # infer a plausible duration of how long the policy will take to enact
        pass

class game:
    def __init__(self, country_name, save_path=None):
        # self.wikipedia = self.load_wikipedia()
        self.state_vars = {
            'year': 2023,
            'week': 1,
            'country': country_name,
            'state_of_the_country': None,
            'sotu': None,
            'past_actions': [],
            'save_path': None,
        }

        if save_path is not None:
            # load save and set state
            with open(save_path, 'r') as f:
                save_json = json.load(f)
            for key, value in save_json.items():
                self.state_vars[key] = value
        else:
            self.state_vars['sotu'] = self.get_starting_state()
            self.state_vars['save_path'] = f'saves/{self.state_vars["country"].lower()}-{self.state_vars["year"]}.json'

    def load_wikipedia(self):
        wikipedia_path = f'data/{self.state_vars["country"].capitalize()} - Wikipedia.html'
        with open(wikipedia_path, 'r') as f:
            html = f.read()
        return partition_html(html)
    
    def get_starting_state(self):
        return llm(f"Write a factual paragraph summarizing the current state of {self.state_vars['country']} in the year {self.state_vars['year']}.").strip()

    def get_prompt(self, policy):
        with open('prompt_template.txt', 'r') as f:
            prompt_template = f.read()
        template = PromptTemplate(
            input_variables=["year", "country", "state_of_the_country", "policy"],
            template=prompt_template
        )
        return template.format(
            year=str(self.state_vars['year']),
            country=self.state_vars['country'],
            state_of_the_country=self.state_vars['sotu'],
            policy=policy
        )
    
    def save(self, save_path):
        save_json = {
            'country': self.state_vars['country'],
            'year': self.state_vars['year'],
            'week': self.state_vars['week'],
            'state': self.state_vars['sotu'],
            'past_actions': self.state_vars['past_actions']
        }
        with open(save_path, 'w') as f:
            json.dump(save_json, f, indent=4)

    def process_action(self, action):
        pass
    
    def play(self):
        while True:
            print(f"{self.state_vars['year']}, Week {self.state_vars['week']}")
            print(self.state_vars['sotu'])
            print("\nAs head of state, name a policy that you would like to implement. Type 'q' to quit.")
            action = input()
            if action == 'q':
                break
            self.state_vars['past_actions'].append(action)
            prompt = self.get_prompt(action)
            self.state_vars['sotu'] = llm(prompt).strip()
            self.save(self.save_path)
            
            if self.state_vars['week'] == 52:
                self.state_vars['year'] += 1
                self.state_vars['week'] = 1
            else:
                self.state_vars['week'] += 1

if __name__ == '__main__':
    game('Afghanistan').play()