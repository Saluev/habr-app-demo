const express = require("express");

app = express();

app.listen(process.env.APP_FRONTEND_PORT);

app.get("*", (req, res) => {
    res.send("Hello, world!")
});
