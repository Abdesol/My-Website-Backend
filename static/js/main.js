function like_or_dislike(id, url){
    var xhr = new XMLHttpRequest();
    
    xhr.open("POST", url);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    data = `{"id":` + id + `}`
    xhr.send(data);

    var response = true;
    xhr.onload = function (){
        if(xhr.status != 200){
            return false;
        }
    }
    return response;
}

function likeBtnStart(button, id, likes){
    if(likes.includes(parseInt(id))){
        button.src = window.location.origin + "/static/img/liked.png"
    }else{
        button.src = window.location.origin + "/static/img/like.png"
    }
}

function loadLocalStorage(arg) {
    var string_liked = localStorage.getItem(arg);
    if(string_liked != null){
        return JSON.parse(string_liked);;
    }
    return [];
}