let open = false;

function toggleChat(){
    document.getElementById("chatbot").style.display = open ? "none" : "flex";
    open = !open;
}

function sendChat(e){
    if(e.key !== "Enter") return;
    let input = document.getElementById("chatInput");
    let msg = input.value.trim();
    if(!msg) return;

    addMsg("You", msg);
    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({message: msg})
    })
    .then(res => res.json())
    .then(data => addMsg("AI", data.reply));
}

function addMsg(sender, text){
    let div = document.createElement("div");
    div.innerHTML = `<b>${sender}:</b> ${text}`;
    document.getElementById("chatBody").appendChild(div);
    document.getElementById("chatBody").scrollTop = 9999;
}
