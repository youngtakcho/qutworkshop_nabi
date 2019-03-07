import json

arr = []
be_arr = []
def open_data(file_name):
    with open(file_name) as f:
        try:
            line = f.readline(4096*1000)
            while line is not None:
                j_data = json.loads(line)
                arr.append(j_data)
                line = f.readline(4096*1000)
        except json.decoder.JSONDecodeError as jde:
            print("--------ERROR-------")
            print(jde)
            print(line)
            print("--------ERROR-------")

f_name = "reviews"
ex_n = ".jl"
for i in range(1,7):
    open_data(f_name+str(i)+ex_n)

be_added = False
for d in arr:
    if "recommended" in d and "text" in d:
        be_arr.append(d)

with open("combined.jl","a+") as f:
    for d in be_arr:
        json.dump(d,f)
        f.write("\n")
