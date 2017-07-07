conn = new Mongo();
db = conn.getDB(STORE_COLLECTION);


db.runCommand({
    createUser: STORE_USER,
    pwd: STORE_PASS,
    roles: ["readWrite", "dbAdmin"]
});
