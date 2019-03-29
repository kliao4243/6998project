var loadingMsgIndex,
    botui = new BotUI('stars-bot'),
    API = 'https://api.github.com/repos/';
    apigClient = apigClientFactory.newClient({
        apiKey: 'ahQu35Lmxn6vIcLkJnlCMadIvsUD8Zfi30F8nUE0'
    });
function init(){
    botui.message.bot({
            delay: 1000,
        content: 'Hi, I am a beautiful chatbot'
        }).then(conversation)
}

function conversation() {
    botui.action.text({
      delay: 1000,
      action: {
        placeholder: 'Enter you wanna say here.'
      }
    }).then(function (res) {
    loadingMsgIndex = botui.message.bot({
      delay: 200,
      loading: true
    }).then(function (index) {
      loadingMsgIndex = index;
      showResponse(res.value)
    });
  });
}

function showResponse(request) {
    let params = {
        "Content-Type": "application/json"
    };
    let body = {
      "request": request
    };
    let additionalParams = {

    };
    let response = "";
    apigClient.chatbotPost(params,body,additionalParams).then(function(result){
      response = JSON.stringify(result["data"]);
    }).then(function(){
        botui.message.update(loadingMsgIndex,{
            content: response
        }).then(conversation);
    });
 // ask again for repo. Keep in loop.
}

init();

