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

export function shouldOpenLinkInNewTab(nativeEvent) {
    // Does user want to open link in a new tab?
    // https://stackoverflow.com/a/20087506/999858
    return (
        nativeEvent.ctrlKey ||
        nativeEvent.shiftKey ||
        nativeEvent.metaKey ||
        (nativeEvent.button && nativeEvent.button === 1)
    );
}

export function areSameStringArrays(a, b) {
    if (a === null || b === null) {
        return (a === null) === (b === null);
    }
    if (a.length !== b.length) {
        return false;
    }
    return a.every((aElem, idx) => aElem === b[idx]);
}
