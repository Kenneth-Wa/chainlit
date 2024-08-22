import os
import importlib
import json
import inspect
from openai import AsyncOpenAI

class FunctionManager:
    def __init__(self):
        self.functions = {}
        self.client = AsyncOpenAI()
        self.load_plugins()

    def load_plugins(self):
        plugins_dir = "plugins"
        for plugin in os.listdir(plugins_dir):
            plugin_dir = os.path.join(plugins_dir, plugin)
            if os.path.isdir(plugin_dir):
                config_file = os.path.join(plugin_dir, "config.json")
                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        config = json.load(f)
                    if config.get("enabled", True):
                        module = importlib.import_module(f"plugins.{plugin}.functions")
                        for name, func in module.__dict__.items():
                            if callable(func) and not name.startswith("_"):
                                self.functions[name] = func

    def generate_functions_array(self):
        functions_array = []
        for name, func in self.functions.items():
            function_info = {
                "name": name,
                "description": func.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                param_info = {"type": "string"}  # Default to string
                if param.annotation != inspect.Parameter.empty:
                    param_info["type"] = param.annotation.__name__
                function_info["parameters"]["properties"][param_name] = param_info
                if param.default == inspect.Parameter.empty:
                    function_info["parameters"]["required"].append(param_name)
            functions_array.append(function_info)
        return functions_array

    async def process_with_openai(self, user_input: str):
        functions = self.generate_functions_array()
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": user_input}],
            functions=functions,
            function_call="auto"
        )
        
        message = response.choices[0].message
        
        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            function_to_call = self.functions[function_name]
            function_response = await function_to_call(**function_args)
            
            second_response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo-0613",
                messages=[
                    {"role": "user", "content": user_input},
                    message,
                    {
                        "role": "function",
                        "name": function_name,
                        "content": str(function_response),
                    },
                ],
            )
            return second_response.choices[0].message.content
        else:
            return message.content