import {
    ADD_PROMISE,
    REMOVE_PROMISE,
    START_FETCHING_CARD,
    FINISH_FETCHING_CARD,
    NAVIGATE,
    FINISH_CREATING_SESSION,
    FINISH_JOINING_ROOM,
    HANDLE_EVENT_STREAM_EVENT
} from "./actions";

function navigate(state, path) {
    if (path === "/") {
        return {
            ...state,
            page: {
                type: "game"
            }
        }
    }
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
        case FINISH_CREATING_SESSION:
            return {
                ...state,
                page: {
                    ...state.page,
                    session: action.sessionData
                }
            };
        case FINISH_JOINING_ROOM:
            return {
                ...state,
                page: {
                    ...state.page,
                    room: action.roomData
                }
            };
        case HANDLE_EVENT_STREAM_EVENT:
            if (action.event.kind === "state" && state.page.session.id === action.sessionId) {
                let gameState = {...action.event};
                delete gameState.kind;
                return {
                    ...state,
                    page: {
                        ...state.page,
                        room: {
                            ...state.page.room,
                            state: gameState
                        }
                    }
                }
            }
            console.warn("Ignoring event stream event:", action.event);
            return state;
        case NAVIGATE:
            return navigate(state, action.path)
    }
    return state;
}
