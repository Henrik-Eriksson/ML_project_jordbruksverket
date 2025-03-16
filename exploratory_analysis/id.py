
import json 

with open("jordbruksverket_data_old.json", "r") as f:
    data = json.load(f)


recordId = 1
for record in data:
    print(recordId)
    record["recordId"] = recordId

    graderingsId = 1
    for gradeMoment in record["graderingstillfalleList"]:
        #print(gradeMoment)
        for gradering in gradeMoment["graderingList"]:
            gradering["gradeId"] = graderingsId
            graderingsId += 1

    recordId += 1

with open("jordbruksverket_data.json", "w") as f:
    json.dump(data,f,indent=4,ensure_ascii=False)

