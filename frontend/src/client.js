import React from 'react'
import {render} from 'react-dom'
import {Provider} from 'react-redux'
import App from './components/app'
import configureStore from './redux/configureStore'

let initialState = {
    page: {
        type: "home"
    }
};
const m = /^\/card\/([^\/]+)$/.exec(location.pathname);
if (m !== null) {
    initialState = {
        page: {
            type: "card",
            cardSlug: m[1]
        },
    }
}

const store = configureStore(initialState);

render(
    <Provider store={store}>
        <App/>
    </Provider>,
    document.querySelector('#app')
);
