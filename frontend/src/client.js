import React from 'react'
import {render} from 'react-dom'
import {Provider} from 'react-redux'
import App from './components/app'
import configureStore from './redux/configureStore'
import {navigate} from "./redux/actions";

let initialState = {
    page: {
        type: "home"
    }
};

const store = configureStore(initialState);
store.dispatch(navigate(location));

render(
    <Provider store={store}>
        <App/>
    </Provider>,
    document.querySelector('#app')
);
