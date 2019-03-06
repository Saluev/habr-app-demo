import express from 'express'
import template from './src/template'
import render from './src/server'

let app = express();

app.use('/dist', express.static('../dist'));

app.get("*", (req, res) => {
    const initialState = {
        page: {
            type: "home"
        }
    };
    const {content, preloadedState} = render(initialState, {pathname: req.url});
    res.send(template("Habr demo app", preloadedState, content));
});

app.listen(process.env.APP_FRONTEND_PORT);
