// Connect to the database.
conn = new Mongo('127.0.0.1:' + PORT);
db = conn.getDB(STORE_COLLECTION);

// Create the user.
db.runCommand({
    createUser: STORE_USER,
    pwd: STORE_PASS,
    roles: ["readWrite", "dbAdmin"]
});

// Show the details to the user to confirm the addition.
printjson(db.getUsers())
