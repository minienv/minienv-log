var app = new Vue({
    el: '#app',
    data: {
        webSocketProtocol: webSocketProtocol,
        webSocket: null,
        webSocketConnected: false,
        webSocketPingTimer: null,
        logs: []
    },
    methods: {
        addLog(log) {
            if (log.all) {
                app.logs = [];
            }
            app.logs.push(log);
            setTimeout(function() {
                app.scrollMessagesToBottom()
            }, 100);
        },
        scrollMessagesToBottom() {
            var e = document.getElementById("log-container");
            e.scrollTop = e.scrollHeight;
        },  
        init() {
            setTimeout(app.onTimer, 1);
        },
        onTimer() {
            if (! app.webSocketConnected) {
                app.connect();
            }
            else {
                app.webSocket.send(JSON.stringify({type: 'ping'}));
            }
            setTimeout(app.onTimer, 5000);
        },
        connect() {
            if ("WebSocket" in window) {
                let webSocketUrl = app.webSocketProtocol + window.location.host;
                app.webSocket = new WebSocket(webSocketUrl);
                app.webSocket.onopen = function() {
                    console.log('Web socket connected.');
                    app.webSocketConnected = true;
                };
                app.webSocket.onmessage = function(evt)  {
                    app.webSocketConnected = true;
                    var data = JSON.parse(evt.data);
                    if (data.type == 'log') {
                        app.addLog({
                            ts: new Date(),
                            log: data.log,
                            all: data.log.all
                        });
                    }
                    else if (data.type == 'ping') {
                        console.log('Received ping.');
                    }
                };
                app.webSocket.onclose = function() {
                    console.log('Websocket closed.');
                    if (app.webSocketConnected) {
                        app.offlineStep = 0;
                    }
                    if (app.awaitingResponse) {
                        app.awaitingResponse = false;
                        app.showOfflineMessage();
                    }
                    app.webSocketConnected = false;
                    app.webSocket = null;
                };
            }
            else {
                alert("WebSocket not supported browser.");
            }
        }
    }
});

(function() {
    // Initialize vue app
    app.init();
})();