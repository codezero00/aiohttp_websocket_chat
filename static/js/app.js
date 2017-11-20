function ChatsPool() {
    var self = this,
        chat_pool = {};
    self.chat_pool = chat_pool;

    this.add_chat = function (chat_client) {
        if (!chat_pool.hasOwnProperty(chat_client.dst_client.id)) {
            chat_pool[chat_client.dst_client.id] = chat_client
        } else {
            console.log('Already in pool');
        }
    };

    this.remove_chat = function (chat_client) {
        delete chat_pool[chat_client.dst_client.id];
    };

    this.get_pool = function () {
        console.log('chat pool requested: ', chat_pool);
        return chat_pool;
    };

    this.get_chat = function (driver) {
        var user_id = driver.id;
        if (!chat_pool.hasOwnProperty(user_id)) {
            chat_pool[user_id] = new ChatClient(driver);
            return chat_pool[user_id]
        }
        return chat_pool[user_id];
    };
}


function send_chat_command(ws, cmd, data) {
    data['cmd'] = cmd;
    console.log('send command', data);
    ws.send(JSON.stringify(data));
}


function ChatClient(driver) {
    var self = this;
    self.dst_client = driver;
    self.have_unreaded_messages = false;


    self._statuses = {
        NOT_CONNECTED: null,
        CONNECTED: 1,
        BROKEN: 2
    };

    self.status = self._statuses.NOT_CONNECTED;
    self.user = null;

    this.init_ws = function () {
        var ws_url = 'ws://' + window.location.host + '/ws';
        console.log('init websocket con to ', ws_url);
        self.ws = new WebSocket(ws_url);
        self.ws.onopen = function () {
            console.log('Connection established');
            send_chat_command(self.ws, 'start', {'dst_user': self.dst_client});
            self.status = self._statuses.CONNECTED;
            ChatClient.chat_pool.add_chat(self);
        };
        self.ws.onerror = function (event) {
            if (event.wasClean) {
                self.status = self._statuses.NOT_CONNECTED;
            } else {
                self.status = self._statuses.BROKEN;
                self.error = 'connection broken'
            }
            ChatClient.chat_pool.remove_chat(self);
            chats.chat_list = Object.values(ChatClient.chat_pool.get_pool());
        };
        self.ws.onmessage = function (event) {
            if (!chats.chat_messages) {
                chats.chat_messages = []
            }
            try {
                var msg_obj = JSON.parse(event.data);
            } catch (e) {
                console.info('unknown data: ', event.data);
            }
            if (chats.active_chat === null) {
                msg_obj.not_readed = true;
                self.have_unreaded = true;
            }
            chats.chat_messages = chats.chat_messages.concat([msg_obj]);
            scroll_chat();
            console.log('message handled', event);
        }
    };

    this.open_chat = function () {
        console.log(arguments);
        if (self.status == self._statuses.CONNECTED) {
            console.log('Already inited ws connection');
            send_chat_command(self.ws, 'start', {'dst_user': self.dst_client});
        } else {
            self.init_ws(arguments);
        }

    };
    this.send_msg = function (text) {
        send_chat_command(self.ws, 'new_msg', {'text': text, 'user_id': self.dst_client.id})
    };
}

ChatClient.chat_pool = new ChatsPool();

chats = {
    active_chat: undefined,
    chat_messages: [],
    chats: ChatClient.chat_pool.chat_pool
};


controller = {
    update_chats: function (e, env) {
        var pool = ChatClient.chat_pool.get_pool();
        console.log('update chat list env=', env, 'with pool=', pool);
        env.data.chat_list = Object.values(pool)
    }
};


convers_template = '<div class="conversation-wrap">' +
    '<div rv-on-click="create_chat_client" class="media conversation" rv-each-chat="chat_list">' +
    '<div class="icon-cont">' +
    '<i class="fa fa-comment-o fa-3" aria-hidden="true"></i>' +
    '</div>' +
    '<div class="media-body">' +
    '<h5 class="media-heading">{chat.dst_client.name}</h5>' +
    '<small rv-show="chat.have_unreaded" >Have new messages!</small>' +
    '</div>' +
    '</div>' +
    '</div>';

rivets.components['drivers-list-item'] = {
    template: function () {
        return convers_template
    },
    initialize: function (el, data) {
        return new driversListController(data);

    }
};

rivets.bind(document.querySelector('#app-chat-container'), {
    controller: controller,
    data: chats,
    active_chat: false,
    messages: [],
    send_msg: function (event, env) {
        chats.active_chat.send_msg(env.data.current_message)
    },
    close_chat: function (event, env) {
        chats.active_chat = null;
    }
});

function scroll_chat() {
    var c = document.querySelector('#chat-window');
    c.scrollTop = c.scrollHeight;
}


function driversListController(attributes) {
    var httpRequest = new XMLHttpRequest(),
        self = this;
    self.attributes = attributes;
    self.chat_pool = chats.chats;

    httpRequest.driver_controller = self;
    httpRequest.onreadystatechange = function (r) {
        if (httpRequest.readyState != 4 || httpRequest.status != 200) return;
        var payload = JSON.parse(httpRequest.responseText);
        this.driver_controller.drivers_list = payload;
        this.driver_controller.chat_list = [];
        for (var i = 0; i < payload.length; i++) {
            var chat = ChatClient.chat_pool.get_chat(payload[i]);
            chat.init_ws();
            this.driver_controller.chat_list = this.driver_controller.chat_list.concat([chat])
        }
    };
    this.init = function () {
        httpRequest.open('GET', '//' + window.location.host + '/api/get_chats', true);
        httpRequest.send();
    };
    this.init();

    this.create_chat_client = function (e, env) {
        chats.chat_messages = [];
        var chat_client = env.chat;
        chat_client.open_chat();
        chats.active_chat = chat_client;
        chats.active_chat.have_unreaded = false;

    };
}


rivets.formatters.json = function (value) {
    return JSON.stringify(value)
};

rivets.formatters.msg_format = function (msg_obj) {
    var text = '';
    text += msg_obj.text;
    return text;
};