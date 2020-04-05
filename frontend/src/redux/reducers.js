import {
    ADD_PROMISE,
    REMOVE_PROMISE,
    START_FETCHING_CARD,
    FINISH_FETCHING_CARD,
    NAVIGATE, SET_COOKIE, START_FETCHING_SEARCH_RESULTS, FINISH_FETCHING_SEARCH_RESULTS
} from "./actions";
import {parseQueryParams} from "../utility";

function navigate(state, link) {
    let m = /^\/card\/([^/]+)$/.exec(link.pathname);
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
    if (link.pathname === "/search") {
        let params = parseQueryParams(link.search || "");
        return {
            ...state,
            page: {
                type: "search",
                query: params.query || "",
                offset: parseInt(params.offset || "0"),
                tags: params.tags && params.tags.split(",").sort() || null,
                isFetching: true,
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
        case START_FETCHING_SEARCH_RESULTS:
            return {
                ...state,
                page: {
                    ...state.page,
                    isFetching: true
                }
            };
        case FINISH_FETCHING_SEARCH_RESULTS:
            return {
                ...state,
                page: {
                    ...state.page,
                    isFetching: false,
                    searchResults: action.searchResults
                }
            };
        case NAVIGATE:
            return navigate(state, action);

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
