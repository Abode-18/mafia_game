let dict = {"id":{"id":{"id":"123","name":"ali"},"id2":{"id":"12","name":"khalid"}},"id2":{"id":{"id":"123","name":"ali"},"id2":{"id":"12","name":"khalid"}}}

i = 0
for (const player of Object.keys(dict["id"])){
    i++;
    console.log(dict["id"][player]["name"])
}