import mmap, json, threading

class YQL:
    def __init__(self):
        # Load json into memory
        self.json_disk_file = open("geoDatabase.json", "r")
        self.json_mem_file = mmap.mmap(self.json_disk_file.fileno(), 0, prot=mmap.PROT_READ)
        self.json_disk_file.close()
        self.json_file = json.load(self.json_mem_file)
        self.generatedFileLock = threading.Lock()

    def getWoeidInQuery(self, q, formatted=False):
        if formatted:
            return q
        try:
            woeid = (q[q.find("(")+1:q.find(")")]).split("=")[1]
        except:
            woeid = (q[q.find("(")+1:q.find(")")]).split("=")[0]
        if "or" in woeid:
            woeid = str(woeid).split(" ")[0]
        return woeid
    
    def getWoeidFromName(self, name):
        print("Getting woeid from name, " + name)
        try:
            result = self.getSimilarName(name)[0]['woeid']
            return result
        except:
            # Generate woeid from name, store the characters in unicode int format for decoding later
            print("Generating woeid from name, " + name)
            with self.generatedFileLock:
                generatedFile = open("generatedWoeids.json", "r+")
                generatedWoeids = json.load(generatedFile)
                woeid = ""
                woeidArray = []
                for letter in name:
                        unicode = str(ord(letter))
                        woeid += unicode
                        woeidArray.append(unicode)
                if not any(woeid in v for v in generatedWoeids):
                    print("Adding woeid to generatedWoeids.json")
                    generatedWoeids.update({woeid: woeidArray})
                    generatedFile.seek(0)
                    generatedFile.write(json.dumps(generatedWoeids))
                    generatedFile.truncate()
                else:
                    print("Woeid already in generatedWoeids.json")
                generatedFile.close()
                return woeid

    def getWoeidName(self, q, formatted=False, nameInQuery=False):
        if not nameInQuery:
            woeid = self.getWoeidInQuery(q, formatted)
        else:
            print(q[q.find("query='")+7:q.find(", ")])
            return q[q.find("query='")+7:q.find(", ")]
        try:
            ret = self.json_file["woeid"][woeid]
        except:
            generatedFile = open("generatedWoeids.json", "r")
            generatedWoeids = json.load(generatedFile)
            name = ""
            for unicodeChar in generatedWoeids[woeid]:
                name += chr(int(unicodeChar))
            ret = name
        return(ret)
       
    def getSimilarName(self, q):
        resultsList = []
        for i in self.json_file["country"].items():
            if q.lower() in i[0].lower():
                resultsList.append({
                    "name": i[0],
                    "iso": self.json_file["country"][i[0]][1],
                    "woeid": self.json_file["country"][i[0]][0],
                    "type": "country"
                })
        for i in self.json_file["city"].items():
            if q.lower() in i[0].lower():
                resultsList.append({
                    "name": i[0],
                    "iso": self.json_file["city"][i[0]][1],
                    "woeid": self.json_file["city"][i[0]][0],
                    "type": "city"
                })
        for i in self.json_file["state"].items():
            if q.lower() in i[0].lower():
                resultsList.append({
                    "name": i[0],
                    "iso": self.json_file["state"][i[0]][1],
                    "woeid": self.json_file["state"][i[0]][0],
                    "type": "state"
                })
        for i in self.json_file["small"].items():
            if q.lower() in i[0].lower():
                resultsList.append({
                    "name": i[0],
                    "iso": self.json_file["small"][i[0]][1],
                    "woeid": self.json_file["small"][i[0]][0],
                    "type": "small"
                })
                
        # Deduplicate
        # for i in resultsList:
        #     print(i)    
        #     if any(o["name"] == i["name"] for o in resultsList):
        #         resultsList.remove(i)

        return resultsList