export function isServerSide() {
    return process.env.APP_ENV !== undefined;
}

export function parseQueryParams(params) {
    if (params === "") {
        return {};
    }
    if (params[0] !== "?") {
        throw "invalid query params string: " + params;
    }
    return params.
        substr(1).
        split("&").
        map(s => s.split("=", 2)).
        reduce((result, keyvalue) => {
            result[keyvalue[0]] = decodeURIComponent(keyvalue[1]);
            return result
        }, {});
}
