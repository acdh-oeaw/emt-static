import json
import os
import glob
import pandas as pd
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import normalize_string
from acdh_cidoc_pyutils import extract_begin_end


file_list = sorted(glob.glob("./data/editions/*.xml"))
data_dir = os.path.join("html", "js-data")
os.makedirs(data_dir, exist_ok=True)
out_file = os.path.join(data_dir, "calendarData.json")
broken = []
events = []
sender = set()
for x in file_list:
    f_id = os.path.split(x)[1].replace(".xml", ".html")
    item = {
        "link": f_id
    }
    doc = TeiReader(x)
    title_node = doc.any_xpath(".//tei:fileDesc/tei:titleStmt/tei:title[@type='main'][1]//text()")[0]

    try:
        sent_date_node = doc.any_xpath("//tei:correspAction/tei:date")[0]
    except IndexError:
        broken.append(f"missing '//tei:correspAction/tei:date' in file: {x}")
        continue
    dates = extract_begin_end(sent_date_node)
    if dates[0]:
        item["date"] = dates[0]
        item["from"] = dates[0]
        item["to"] = dates[1]
        if dates[0] == dates[1]:
            item["range"] = False
        else:
            item["range"] = True
        item["label"] = normalize_string(title_node)
        sender_name = normalize_string(doc.any_xpath(".//tei:correspAction[@type='sent']/tei:persName//text()")[0])
        sender_id = doc.any_xpath(".//tei:correspAction[@type='sent']/tei:persName/@ref")[0]
        item["kind"] = f"{sender_id[1:]}.html"
        item["sender"] = {
            "label": sender_name,
            "link": f"{sender_id[1:]}.html"
        }
        events.append(item)
    else:
        pass
    for y in doc.any_xpath("//tei:body//tei:date[@type='letter']"):
        extra_item = {
            "link": False,
            "label": "Brief_erschlossen"
        }
        ex_date = extract_begin_end(y)
        extra_item["date"] = ex_date[0]
        extra_item["kind"] = "Brief_erschlossen"
        extra_item["from"] = ex_date[0]
        extra_item["to"] = ex_date[1]
        extra_item["ref_by"] = f_id
        events.append(extra_item)

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)


df = pd.DataFrame(events)
df.to_csv("hansi.csv", index=False)