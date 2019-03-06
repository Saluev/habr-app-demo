export default function template(title, initialState, content) {
    let page = `
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>${title}</title>
            </head>
            <body>
                <div id="app">${content}</div>
                <script>
                   window.__STATE__ = ${JSON.stringify(initialState)}
                </script>
                <script src="/dist/client.js"></script>
            </body>
        </html>
      `;
    return page;
}
