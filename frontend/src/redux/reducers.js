import {
    ADD_PROMISE,
    REMOVE_PROMISE,
    START_FETCHING_CARD,
    FINISH_FETCHING_CARD,
    NAVIGATE, SET_COOKIE
} from "./actions";

function navigate(state, path) {
    let m = /^\/card\/([^/]+)$/.exec(path);
    if (m !== null) {
        return {
            ...state,
            page: {
                type: "card",
                cardSlug: m[1],
                isFetching: true
            }
        };
    }
    return state
}

export default function root(state = {}, action) {
    switch (action.type) {
        case ADD_PROMISE:
            return {
                ...state,
                promises: [...state.promises, action.promise]
            };
        case REMOVE_PROMISE:
            return {
                ...state,
                promises: state.promises.filter(p => p !== action.promise)
            };
        case START_FETCHING_CARD:
            return {
                ...state,
                page: {
                    ...state.page,
                    isFetching: true
                }
            };
        case FINISH_FETCHING_CARD:
            return {
                ...state,
                page: {
                    ...state.page,
                    isFetching: false,
                    cardData: action.cardData
                }
            };
        case NAVIGATE:
            return navigate(state, action.path);

        case SET_COOKIE:
            // This is a very, very bad way to handle cookies on server-side.
            // We should start using something like `cookie` package.
            let cookie = state.cookie;
            for (let item of action.cookie) {
                let keyValue = item.split(";")[0];
                cookie = cookie ? cookie + "; " + keyValue : keyValue;
            }
            return {
                ...state,
                cookie: cookie,
                cookieToSet: [
                    ...state.cookieToSet,
                    ...action.cookie,
                ]
            }
    }
    return state;
}
