export function isServerSide() {
    return process.env.APP_ENV !== undefined;
}
