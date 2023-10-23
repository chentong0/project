from utils.lm import LM
import openai
import sys
import time
import os
import numpy as np
import logging

class OpenAIModel(LM):

    def __init__(self, model_name, cache_file=None, model_mode="chat_gpt", api_type="openai", save_interval=100):
        self.model_name = model_name
        self.model_mode = model_mode
        self.api_type = api_type
        super().__init__(cache_file, save_interval)

    def load_model(self):
        # load api key
        if self.api_type == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            assert isinstance(api_key, str), "Please provide a valid OpenAI API Key."
            openai.api_key = api_key.strip()
        elif self.api_type == "azure":
            openai.api_type = 'azure'
            openai.api_version = "2023-03-15-preview"
            openai.api_key = os.environ.get("M_OPENAI_API_KEY") # your api key
            openai.api_base =  os.environ.get("M_OPENAI_API_BASE") # your api base

        self.model = self.model_name

    def _generate(self, prompt, temperature=0.0, max_tokens=100):
        # return a tuple of string (generated text) and metadata (any format)
        # This should be about generating a response from the prompt, no matter what the application is
        if self.model_mode == "chat_gpt":
            # Construct the prompt send to ChatGPT
            if isinstance(prompt, str):
                message = [{"role": "user", "content": prompt}]
            elif isinstance(prompt, list):
                message = prompt
            else:
                raise ValueError("Prompt must be a string or a list of strings")
            # Call API
            output, response = call_gpt(self.model_mode, self.api_type, self.model_name, message, max_tokens=max_tokens, temperature=temperature)
            # Get the output from the response
            return output, response
        elif self.model_mode == "instruct_gpt":
            # Call API
            output, response = call_gpt(self.model_mode, self.api_type, self.model_name, prompt, max_tokens=max_tokens, temperature=temperature)
            # Get the output from the response
            return output, response
        else:
            raise NotImplementedError()

def call_gpt(model_mode, api_type, model_name, prompt_or_message, max_tokens=100, temperature=0.0):
    # call GPT-3 API until result is provided and then return it
    output, response = None, None
    for n_tries in range(5):
        try:
            if model_mode == "chat_gpt":
                if api_type == "openai":
                    configure = {"model": model_name, "messages": prompt_or_message, 
                        "max_tokens": max_tokens, "temperature": temperature}
                elif api_type == "azure":
                    configure = {"engine": model_name, "messages": prompt_or_message, 
                        "max_tokens": max_tokens, "temperature": temperature}
                else:
                    raise ValueError(f'api_type {api_type} not supported.')
                response = openai.ChatCompletion.create(**configure)
                output = response["choices"][0]["message"]["content"]
            elif model_mode == "instruct_gpt":
                if api_type == "openai":
                    configure = {"model": model_name, "prompt": prompt_or_message, 
                        "max_tokens": max_tokens, "temperature": temperature}
                elif api_type == "azure":
                    configure = {"engine": model_name, "prompt": prompt_or_message, 
                        "max_tokens": max_tokens, "temperature": temperature}
                else:
                    raise ValueError(f'api_type {api_type} not supported.')
                response = openai.Completion.create(**configure)
                output = response["choices"][0]["text"]
        except Exception as e:
            # print(message)
            if e == openai.error.InvalidRequestError:
                # something is wrong: e.g. prompt too long
                logging.critical(f"InvalidRequestError\nPrompt passed in:\n\n{prompt_or_message}\n\n")
                assert False
            import re
            # example: after 9 second
            pattern = re.compile(r"after (\d+) second")
            match = pattern.search(str(e))
            wait_time = int(match.group(1)) if match else 2 ** n_tries
            logging.error(f"API error: {e} ({n_tries}). Waiting {wait_time} sec")
            if response is not None:
                logging.error(f"Response: {response}")
            time.sleep(wait_time)
    if not isinstance(response, dict):
        raise ValueError(f"Response is not a dict: {response}")
    return output, response
