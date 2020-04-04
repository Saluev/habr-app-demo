import express from 'express'
import template from './src/template'
import render from './src/server'

let app = express();

app.use('/dist', express.static('../dist'));

app.get("*", (req, res) => {
    const initialState = {
        page: {
            type: "home"
        },
        promises: [],
        cookie: req.headers.cookie,
        cookieToSet: [],
    };
    let params = "?" + Object.keys(req.query).map(key => key + "=" + encodeURIComponent(req.query[key])).join("&");
    render(initialState, {href: req.url, pathname: req.path, search: params}).then(result => {
        const {content, preloadedState} = result;
        const response = template("Habr demo app", preloadedState, content);
        const cookieToSet = preloadedState.cookieToSet;
        delete preloadedState.cookie;
        delete preloadedState.cookieToSet;
        for (let c of cookieToSet) {
            res.set("Set-Cookie", c);
        }

        res.send(response);
    }, (reason) => {
        console.log(reason);
        res.status(500).send("Server side rendering failed!");
    });
});

app.listen(process.env.APP_FRONTEND_PORT);
