import React from 'react'
import {renderToString} from 'react-dom/server'
import {Provider} from 'react-redux'
import App from './components/app'
import {navigate} from "./redux/actions";
import configureStore from "./redux/configureStore";

function hasPromises(state) {
    return state.promises.length > 0
}

export default async function render(initialState, url) {
    const store = configureStore(initialState);
    store.dispatch(navigate(url));

    let app = (
        <Provider store={store}>
            <App/>
        </Provider>
    );

    renderToString(app);

    let preloadedState = store.getState();
    while (hasPromises(preloadedState)) {
        await preloadedState.promises[0];
        preloadedState = store.getState()
    }

    let content = renderToString(app);

    return {content, preloadedState};
};
