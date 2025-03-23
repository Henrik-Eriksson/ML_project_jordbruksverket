
import json 

#Adds unique recordId to each record and gradeId to each grading entry, then saves the updated data to a new JSON file.
with open("../jordbruksverket_data/jordbruksverket_data.json", "r") as f:
    data = json.load(f)

recordId = 1
for record in data:
    print(recordId)
    record["recordId"] = recordId

    graderingsId = 1
    for gradeMoment in record["graderingstillfalleList"]:
        for gradering in gradeMoment["graderingList"]:
            gradering["gradeId"] = graderingsId
            graderingsId += 1

    recordId += 1

with open("jordbruksverket_data.json", "w") as f:
    json.dump(data,f,indent=4,ensure_ascii=False)

