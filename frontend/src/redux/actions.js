import {areSameStringArrays, isServerSide} from "../utility";
import fetch from "./fetch";

export const SET_COOKIE = "SET_COOKIE";
export const ADD_PROMISE = "ADD_PROMISE";
export const REMOVE_PROMISE = "REMOVE_PROMISE";
export const START_FETCHING_CARD = "START_FETCHING_CARD";
export const FINISH_FETCHING_CARD = "FINISH_FETCHING_CARD";
export const START_FETCHING_SEARCH_RESULTS = "START_FETCHING_SEARCH_RESULTS";
export const FINISH_FETCHING_SEARCH_RESULTS = "FINISH_FETCHING_SEARCH_RESULTS";
export const NAVIGATE = "NAVIGATE";

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
        let promise = fetch(url, {}, dispatch, getState)
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

function startFetchingSearchResults() {
    return {
        type: START_FETCHING_SEARCH_RESULTS
    };
}

function finishFetchingSearchResults(json, query, offset, tags) {
    return {
        type: FINISH_FETCHING_SEARCH_RESULTS,
        searchResults: {
            query: query,
            offset: offset,
            tags: tags,
            ...json
        }
    };
}

function fetchSearchResults() {
    return (dispatch, getState) => {
        dispatch(startFetchingSearchResults());
        let state = getState();
        let query = state.page.query;
        let offset = state.page.offset;
        let tags = state.page.tags;
        let url = apiPath() + "/cards/search";
        let promise = fetch(url, {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "query": query,
                "offset": offset,
                "tags": tags,
            })
        }, dispatch, getState)
            .then(response => response.json())
            .then(json => {
                dispatch(finishFetchingSearchResults(json, query, offset, tags));
                dispatch(removePromise(promise));
            });
        return dispatch(addPromise(promise));
    };
}

export function fetchSearchResultsIfNeeded() {
    return (dispatch, getState) => {
        let state = getState().page;
        let query = state.query;
        let offset = state.offset;
        let tags = state.tags;
        if (state.searchResults === undefined ||
            state.searchResults.query !== query ||
            state.searchResults.offset !== offset ||
            !areSameStringArrays(state.searchResults.tags, tags)) {
            return dispatch(fetchSearchResults());
        }
    }
}

export function navigate(link, dontPushState) {
    if (!isServerSide() && !dontPushState) {
        history.pushState({
            pathname: link.pathname,
            href: link.href,
            search: link.search
        }, "", link.href);
    }
    return {
        type: NAVIGATE,
        pathname: link.pathname,
        search: link.search,
    }
}
