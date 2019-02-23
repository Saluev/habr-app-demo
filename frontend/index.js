import express from 'express'
import template from './src/template'

let app = express();

app.use('/dist', express.static('../dist'));

app.get("*", (req, res) => {
    res.send(template("Habr demo app"));
});

app.listen(process.env.APP_FRONTEND_PORT);
