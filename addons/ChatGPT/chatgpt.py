import openai
import datetime

class ChatGPT():
    def __init__(self, api_key):
        openai.api_key = api_key
        # 设置代理：192.168.137.1:7890
        openai.proxy = "http://192.168.137.1:7890"

    def get_completion(self, prompt, model="gpt-3.5-turbo-16k-0613"):
        message = [
            {"role": "user", "content": prompt}
        ]
        print("Create OpenAI Chat Completion")
        today = datetime.date.today().strftime("%Y年%m月%d日 %H:%M")
        response = openai.ChatCompletion.create(
            model=model,
            messages=message,
            # temperature=0,
            # max_tokens=1000,
            # top_p=1,
            # frequency_penalty=0, 
            # presence_penalty=0,
            
            functions=[{
                "name":"set_todo",
                "description":f"设置待办事项。日期如: `2021年6月13日 23:00` 或者 `2021-6-13 23:00` 或者 明天。（绝对日期和相对日期都行, 如果没有具体的小时和分钟，那么就指定为08时00分.）已知今天的日期是{today}。",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "content":{"type":"string","description":"待办事项内容"},
                        "date":{"type":"string","description":f"待办事项的截止日期。格式必须是`YYYY年MM月DD日 HH:mm`"},
                    },
                    "required":["content","date"],
                },
            },
            {
                "name":"view_todo",
                "description":f"根据给定的时间查看待办事项。已知今天的日期是{today}。如果给定的时间是`今天`,`明天`之类的相对时间，则转换成格式是`YYYY年MM月DD日`的时间。如果没有给定时间或者表述不清晰或者其他原因，那么就查看所有待办事项",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "date":{"type":"string","description":f"格式必须是`YYYY年MM月DD日`。返回的待办事项日期。"},
                        "all":{"type":"boolean","description":f"是否查看所有待办事项。默认为`false`"},
                    },
                    "required":["date","all"],
                },
            }
            
            ],
            function_call="auto" 
        )
        response_message = response["choices"][0]["message"]
        return response_message

    def set_model(self, model):
        self.model = model

    def set_temperature(self, temperature):
        self.temperature = temperature

    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens

    def set_chat_log(self, chat_log):
        self.chat_log = chat_log