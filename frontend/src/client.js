import React from 'react'
import {hydrate} from 'react-dom'
import {Provider} from 'react-redux'
import App from './components/app'
import configureStore from './redux/configureStore'

const store = configureStore(window.__STATE__);

hydrate(
    <Provider store={store}>
        <App/>
    </Provider>,
    document.querySelector('#app')
);
