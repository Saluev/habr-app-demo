import React from 'react'
import {renderToString} from 'react-dom/server'
import {Provider} from 'react-redux'
import App from './components/app'
import {navigate} from "./redux/actions";
import configureStore from "./redux/configureStore";


export default function render(initialState, url) {
    const store = configureStore(initialState);
    store.dispatch(navigate(url));

    let app = (
        <Provider store={store}>
            <App/>
        </Provider>
    );

    let content = renderToString(app);
    let preloadedState = store.getState();

    return {content, preloadedState};
};
