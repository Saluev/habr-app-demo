import fetch from "cross-fetch";
import {isServerSide} from "../utility";
import {SET_COOKIE} from "./actions";

export default function(url, init, dispatch, getState) {
    init = {...init, "credentials": "include"};
    if (isServerSide()) {
        let headers = {...init.headers};
        let state = getState();
        if (state.cookie) {
            headers["Cookie"] = state.cookie;
        }
        return fetch(url, {...init, headers: headers}).then(resp => {
            if (resp.headers.raw()["set-cookie"]) {
                dispatch({
                    type: SET_COOKIE,
                    cookie: resp.headers.raw()["set-cookie"],
                })
            }
            return resp
        })
    }
    return fetch(url, init);
}
