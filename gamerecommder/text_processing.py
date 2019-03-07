import json
import re

# emoji_pattern = re.compile("["
#         u"\U0001F600-\U0001F64F"  # emoticons
#         u"\U0001F300-\U0001F5FF"  # symbols & pictographs
#         u"\U0001F680-\U0001F6FF"  # transport & map symbols
#         u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
#                            "]+", flags=re.UNICODE)

emoji = re.compile(u'('
                   u'\ud83c[\udf00-\udfff]|'
                   u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                   u'[\u2600-\u26FF\u2700-\u27BF])+',
                   re.UNICODE)
keys = set()
with open("products_all2.jl","r") as f:
    # with open("rep.txt","a+") as ff:
        for line in f:
            try:
                data = json.loads(line)
                # text:str = data["text"]
                # preprocessed = emoji.sub(r'',text) +"\n"
                # data["text"] = preprocessed
                keys = keys.union(data.keys())
                # json.dump(data,ff)
                # ff.write("\n")
            except json.decoder.JSONDecodeError as e:
                continue
print(keys)


