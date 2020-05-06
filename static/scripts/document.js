$(document).ready(function () {
    updater.start();
    // init tree and bind events
    $('#xml_content').tree({
        data: [],
        autoOpen: true,
        onCanSelectNode: function(node) {
            // if node does not have id, then it is cannot be selected.
            return node.id;
        }
    });
    $('#xml_content').bind('tree.select', onNodeClick);

    // this is called so that it loads the tree at the beginning
    updateContent();
});

/**
 * if no node is selected, then make all buttons disabled
 * (but not set_name,load,save,delete because they are not related to nodes.)
 * @param available
 */
function changeButtonAvailability(available) {
    // node class is added only the forms' submit buttons which need id as an input.
    $('.node').prop('disabled', !available);
    if (available === false) {
        // make input values empty.
        $('input[name=id]').val("");
    }
}

function onNodeClick(event) {
    const node = event.node;
    if (node == null) { // case 1: click on a selected-node. So there is no selected node now.
        changeButtonAvailability(false);
    }
    else if (node.id) {
        $('input[name=id]').val(node.id);
        changeButtonAvailability(true);
    }
}

const updater = {  // web socket object gets updatemodel requests
    socket: null,

    start: function () {
        var url = "ws://" + 'localhost:9000' + "/documents";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function (event) {
            if (JSON.parse(event.data).redirect) { // should be redirected
                location.replace('/')
            }
            if (JSON.parse(event.data).error) { // error, no need to update
                showError(JSON.parse(event.data).error);
            } else { // when a new message is received, parse and update model
                updateContent();
            }
        };
        updater.socket.onopen = function () {
            const dbdoc_id = document.getElementById('dbdocId').value;
            const session_key = document.getElementById('sessionKey').value;
            const json = {};
            json['id'] = dbdoc_id;
            json['operation'] = 'add';
            json['session_key'] = session_key;
            updater.socket.send(JSON.stringify(json));

        }
    }
};

function updateContent() {

    const dbdoc_id = document.getElementById('dbdocId').value;
    const url = '/api/get_document/json/' + dbdoc_id;

    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

    $.getJSON(url, function (data) {

        document.getElementById('doc_name').innerHTML = 'Document - ' + data.doc_name;
        document.getElementById('page_title').innerHTML = data.doc_name;
        const json_xml = JSON.parse(data.json_xml);

        $('#xml_content').tree('loadData', [json_xml]);
        // after new data is loaded, there won't be a selected node
        changeButtonAvailability(false);
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showError(error) {
    const notifymess = error;
    const notifybg = "#ffa0a0";

    // show notification message coming from server bottom right
    $("#notification").text(notifymess)
        .css({
            position: "absolute", bottom: "5px",
            right: "5px", padding: "15px", "border-radius": "8px",
            "box-shadow": "4px 4px 2px #808080", 'background-color': notifybg
        })
        .fadeIn().delay(3000).slideUp(); // show for 3 seconds and disappear
}

