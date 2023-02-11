import langchain
from langchain.llms import OpenAI
from unstructured.partition.html import partition_html
from langchain import PromptTemplate
from policy import policy
import json

with open('/Users/jasper/oai.txt', 'r') as f:
    key = f.read()

llm = OpenAI(temperature=0.5, openai_api_key=key)

with open('prompts/base_prompt.txt', 'r') as f:
    base_prompt = f.read()

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
            'active_actions': [],
            'save_path': None,
            'health': 100,
        }

        if save_path is not None:
            # load save and set state
            with open(save_path, 'r') as f:
                save_json = json.load(f)
            for key, value in save_json.items():
                self.state_vars[key] = value
        else:
            self.state_vars['sotu'] = self.get_starting_state()
            self.state_vars['health'] = self.get_health()
            self.state_vars['save_path'] = f'saves/{self.state_vars["country"].lower()}-{self.state_vars["year"]}.json'

    def load_wikipedia(self):
        wikipedia_path = f'data/{self.state_vars["country"].capitalize()} - Wikipedia.html'
        with open(wikipedia_path, 'r') as f:
            html = f.read()
        return partition_html(html)
    
    def get_starting_state(self):
        return llm(f"Write a factual paragraph summarizing the current state of {self.state_vars['country']} in the year {self.state_vars['year']}.").strip()

    def get_prompt(self, policy):
        with open('prompts/prompt_template.txt', 'r') as f:
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
        # serialize all policies in active_actions to JSON
        for i, policy in enumerate(self.state_vars['active_actions']):
            self.state_vars['active_actions'][i] = policy.toJSON()
        with open(save_path, 'w') as f:
            json.dump(self.state_vars, f, indent=4)

    def get_action_duration(self, action):
        """
        Get the execution duration of a proposed action in years and weeks
        """
        with open('prompts/action_length_prompt.txt', 'r') as f:
            length_prompt = f.read()
        full_prompt = base_prompt + length_prompt
        template = PromptTemplate(
            input_variables=["year", "country", "state_of_the_country", "example_json", "policy"],
            template=full_prompt
        )
        example_json = """{
            "years": 1,
            "weeks": 30
        }"""
        prompt = template.format(
            year=str(self.state_vars['year']),
            country=self.state_vars['country'],
            state_of_the_country=self.state_vars['sotu'],
            example_json=example_json,
            policy=action
        )
        output = llm(prompt).strip()
        # ensure that the output has double quotes
        output = json.loads(output)
        return int(output['years']), int(output['weeks'])
    
    def get_health(self):
        """
        Get the health of the country
        """
        with open('prompts/health.txt', 'r') as f:
            health_prompt = f.read()
        full_prompt = base_prompt + health_prompt
        template = PromptTemplate(
            input_variables=["year", "country", "state_of_the_country"],
            template=full_prompt
        )
        prompt = template.format(
            year=str(self.state_vars['year']),
            country=self.state_vars['country'],
            state_of_the_country=self.state_vars['sotu'],
        )
        output = llm(prompt).strip()
        return int(output)

    def play(self, actions_list=None):
        while True:
            print(f"{self.state_vars['year']}, Week {self.state_vars['week']}")
            print(self.state_vars['sotu'])
            print(f"Health: {self.state_vars['health']}")
            print("\nAs head of state, name a policy that you would like to implement. Type 'q' to quit.")

            if not actions_list:
                action = input(prompt=">")
            else:
                action = actions_list.pop(0)
                print(action)
            if action == 'q':
                self.save(self.state_vars['save_path'])
                break

            # process action
            implementation_years, implementation_weeks = self.get_action_duration(action)
            self.state_vars['active_actions'].append(
                policy(action, self.state_vars['year'], self.state_vars['week'], implementation_years, implementation_weeks)
            )
            self.state_vars['past_actions'].append(action)
            prompt = self.get_prompt(action)
            self.state_vars['sotu'] = llm(prompt).strip()
            self.state_vars['health'] = self.get_health()
            if self.state_vars['health'] <= 0:
                print(f"{self.state_vars['country']} has failed! Game over")
                break
            
            if self.state_vars['week'] == 52:
                self.state_vars['year'] += 1
                self.state_vars['week'] = 1
            else:
                self.state_vars['week'] += 1
            
            # remove expired actions
            self.state_vars['active_actions'] = [action for action in self.state_vars['active_actions'] if not action.is_expired(self.state_vars['year'], self.state_vars['week'])]

if __name__ == '__main__':
    game = game('Afghanistan')
    game.play()