class ChatGPT():
    def __init__(self, model_name, prompt, context, client):
        self.model_name = model_name
        self.prompt = prompt
        self.context = context
        self.client = client
        print(f"ChatGPT class initialized with model {model_name}")
    
    def chat_model(self):
        self.context.append({"role": "user", "content": self.prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.context
            )

            answer = response.choices[0].message.content.strip()
            self.context.append({"role": "assistant", "content": answer})

            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            return [answer, self.context, input_tokens, output_tokens]
        
        except Exception as e:
            print(f"API Error: {e}")
            return [None, None]
