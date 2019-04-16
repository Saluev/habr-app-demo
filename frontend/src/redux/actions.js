import {isServerSide} from "../utility";
import fetch from "cross-fetch";

export const ADD_PROMISE = "ADD_PROMISE";
export const REMOVE_PROMISE = "REMOVE_PROMISE";
export const START_FETCHING_CARD = "START_FETCHING_CARD";
export const FINISH_FETCHING_CARD = "FINISH_FETCHING_CARD";
export const NAVIGATE = "NAVIGATE";
export const FINISH_CREATING_SESSION = "FINISH_CREATING_SESSION";
export const FINISH_JOINING_ROOM = "FINISH_JOINING_ROOM";
export const HANDLE_EVENT_STREAM_EVENT = "HANDLE_EVENT_STREAM_EVENT";
export const HANDLE_EVENT_STREAM_ERROR = "HANDLE_EVENT_STREAM_ERROR";

function apiPath() {
    if (isServerSide()) {
        return "http://backend:40001/api/v1";
    }
    return "http://localhost:40001/api/v1";
}

function addPromise(promise) {
    return {
        type: ADD_PROMISE,
        promise: promise
    };
}

function removePromise(promise) {
    return {
        type: REMOVE_PROMISE,
        promise: promise,
    };
}

function startFetchingCard() {
    return {
        type: START_FETCHING_CARD
    };
}

function finishFetchingCard(json) {
    return {
        type: FINISH_FETCHING_CARD,
        cardData: json
    };
}

function fetchCard() {
    return (dispatch, getState) => {
        dispatch(startFetchingCard());
        let url = apiPath() + "/card/" + getState().page.cardSlug;
        let promise = fetch(url)
            .then(response => response.json())
            .then(json => {
                dispatch(finishFetchingCard(json));
                dispatch(removePromise(promise));
            });
        return dispatch(addPromise(promise));
    };
}

export function fetchCardIfNeeded() {
    return (dispatch, getState) => {
        let state = getState().page;
        if (state.cardData === undefined || state.cardData.slug !== state.cardSlug) {
            return dispatch(fetchCard());
        }
    };
}

function joinRoom(sessionID) {
    return (dispatch, getState) => {
        let url = apiPath() + "/session/" + sessionID + "/join";
        return fetch(url)
            .then(response => response.json())
            .then(json => {
                dispatch({
                    type: FINISH_JOINING_ROOM,
                    roomData: json,
                });
            })
    }
}

export function createSession() {
    return (dispatch, getState) => {
       let url = apiPath() + "/session/create";
       return fetch(url)
           .then(response => response.json())
           .then(json => {
               dispatch({
                   type: FINISH_CREATING_SESSION,
                   sessionData: json
               });
               dispatch(joinRoom(json.id));
           });
    }
}

export function requestEvents(sessionId) {
    return (dispatch, getState) => {
        let url = apiPath() + "/session/" + sessionId + "/events";
        let eventSource = new EventSource(url);
        console.debug("Created event source:", eventSource);
        eventSource.onmessage = function(e) {
            console.debug("Got message via event source:", e);
            dispatch({
                type: HANDLE_EVENT_STREAM_EVENT,
                sessionId: sessionId,
                event: JSON.parse(e.data)
            });
        };
        eventSource.onerror = function(e) {
            console.warn("Got error from event source:", e);
            dispatch({
                type: HANDLE_EVENT_STREAM_ERROR,
                sessionId: sessionId,
                error: e
            });
        };
        // TODO save event source in state somewhere, to be able to close it
        return {};
    }
}

export function submitAction(action) {
    return (dispatch, getState) => {
        let url = apiPath() + "/session/" + getState().page.session.id + "/action";
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(action)
        }).then((response) => {
            console.debug("API /action response:", response)
        }, (response) => {
            console.error("API /action error:", response)
        });
    }
}

export function navigate(link, dontPushState) {
    if (!isServerSide() && !dontPushState) {
        history.pushState({
            pathname: link.pathname,
            href: link.href
        }, "", link.href);
    }
    return {
        type: NAVIGATE,
        path: link.pathname
    }
}
